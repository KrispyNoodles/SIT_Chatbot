import chainlit as cl
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableLambda

from prompts import system_prompt
from tools.redis_tool import redis_tool
from tools.google_tool import google_tool
from config import model, tool_usage_log
from utils import summary_fn


# a potentional function yet to be built that retrieves the "thread_id"
config_no = "abc123"

# creating a nested dictionary with a key called "thread_id"
config = {"configurable": {"thread_id": config_no}}

# Initialising a memory which is used to save and retrieve conversation state to enable
# continuity in the chatbot's interactions
memory = MemorySaver()

# A list that holds all the tools that the agent can use
tools = [redis_tool, google_tool]

# This sets up a REACT agent that will handle the overall task execution
agent_executor = create_react_agent(model, tools, checkpointer=memory, debug=False)

# declaration of system prompt
messages =  [SystemMessage(content=system_prompt)]

# tool is used when to see which tools are being used
@cl.step(type="tool")
async def tool():
    
    if tool_usage_log:
        tool_info = tool_usage_log[-1]
        return tool_info
    
    else:
        tool_info =("No tool usage at all.")
        return tool_info
    
# on_chat_start decorator is used when the chat bot has started
@cl.on_chat_start
async def on_chat_start():
    sentence = "Hello!! Welcome to this chatbot"
    await cl.Message(content=sentence).send()
    messages.append(AIMessage(content=sentence))

@cl.on_message
async def on_message(message: cl.Message):

    global messages
    
    # appending the human's message
    messages.append(HumanMessage(content=message.content))
    
    response = agent_executor.invoke(
        
        # Including the system prompt and and message entered by the user to be included into the prompt
        {"messages": messages},

        # Indicating the chat conversation history of the user
        config=config,
    )

    # assigning the result of the output
    result = response["messages"][-1]

    # checking if the result is an AIMessage, to be printed by the UI
    if isinstance(result, AIMessage):
        
        await tool()
        await cl.Message(content=result.content).send()
        
        # appending the result
        messages.append(AIMessage(content=result.content))

    # Summmary function implementation
    summary_runnable = RunnableLambda(summary_fn)
    messages = summary_runnable.invoke(messages)
    
    print(f"Length of messages is {len(messages)}")