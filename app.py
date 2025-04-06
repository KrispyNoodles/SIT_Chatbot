import chainlit as cl
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableLambda

from prompts import system_prompt, get_suggestion_prompt, default_suggestions, welcome_message
from tools.redis_tool import redis_tool
from tools.google_tool import google_tool
from config import model, tool_usage_log, mini_model
from utils import summary_fn, generate_actions


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
messages = [SystemMessage(content=system_prompt), AIMessage(content=welcome_message)]

# buttons of suggestions
@cl.action_callback("action_button_1")
async def on_action(action):
    await process_suggestion(action.value, action)

@cl.action_callback("action_button_2")
async def on_action(action):
    await process_suggestion(action.value, action)

# decorator for tools being used
@cl.step(type="tool")
async def tool():
    
    if tool_usage_log:
        tool_info = "\n".join(tool_usage_log)
    
    else:
        tool_info = ("No tool usage at all.")
    
    return tool_info
    
# on_chat_start decorator is used when the chat bot has started
@cl.on_chat_start
async def on_chat_start():
    global messages
        
    await cl.Message(content=welcome_message).send()

    text = "Just type your question or click on the prompt suggestions below, and I’ll do my best to assist you! 🚀"
    messages.append(AIMessage(content=text))

    actions = generate_actions(default_suggestions)
    await cl.Message(content=text, actions=actions).send()

@cl.on_message
async def on_message(message: cl.Message):

    global messages
    
    # appending the human's message
    messages.append(HumanMessage(content=message.content))
    
    # Generating the response
    # stream: Accepts an input and returns a generator that yields outputs.
    async for event in agent_executor.astream(
        {"messages": messages}, 
        config=config,
        stream_mode="values",
        ):
            # Extract the last message from the response
            result = event["messages"][-1]

            if isinstance(result, AIMessage) and result.content != "":
                
                # displaying which tool was used
                await tool()
                
                # appending the chatbot's response
                messages.append(AIMessage(content=result.content))
                
                # sending the chatbot's message and the user's message into the system prompt
                formatted_prompt= get_suggestion_prompt(result.content, message.content)
                
                # giving suggestions based off the recent reply from the llm
                response = mini_model.invoke(formatted_prompt)
                suggestions = response.content.split("\n")[:2]
                                                    
                actions = generate_actions(suggestions)

                await cl.Message(content=result.content, actions=actions).send()

    # Summmary function implementation
    summary_runnable = RunnableLambda(summary_fn)
    messages = summary_runnable.invoke(messages)
    
    print(f"Length of messages is {len(messages)}")

# Action button callbacks
async def process_suggestion(suggestion, action):
    
    # removing the buttons
    await action.remove()
    
    # Show the selected suggestion as if the user typed it
    user_message = cl.Message(content=f"User selected: {suggestion}")
    await user_message.send()

    # Pass it to on_message decorator for processing
    await on_message(cl.Message(content=suggestion))