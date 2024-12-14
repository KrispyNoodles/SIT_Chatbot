import chainlit as cl
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from prompts import system_prompt
from tools.redis_tool import redis_tool
from tools.google_tool import google_tool
from config import model


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
agent_executor = create_react_agent(model, tools, checkpointer=memory, debug=True)

# on_chat_start decorator is used when the chat bot has started
@cl.on_chat_start
async def on_chat_start():
    sentence = "Hello!! Welcome to this chatbot"
    await cl.Message(content=sentence).send()

@cl.on_message
async def on_message(message: cl.Message):
    
    response = agent_executor.invoke(
        
        # Including the system prompt and and message entered by the user to be included into the prompt
        {"messages": [AIMessage(system_prompt), HumanMessage(content=message.content)]},

        # Indicating the chat conversation history of the user
        config=config,
    )

    # assigning the result of the output
    result = response["messages"][-1]

    # checking if the result is an AIMessage, to be printed by the UI
    if isinstance(result, AIMessage):
        print(result.content)
        await cl.Message(content=result.content).send()
