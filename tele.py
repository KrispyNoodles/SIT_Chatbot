from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from config import model
from tools.redis_tool import redis_tool
from tools.google_tool import google_tool
from utils import get_user_config, emoji_printer, summary_fn
from langchain_core.runnables import RunnableLambda
from config import bot
from prompts import tele_system_prompt, sticker_prompt

# name of telegram handle is @SIT_izen_bot

memory = MemorySaver()

# A list that holds all the tools that the agent can use
tools = [redis_tool, google_tool]

# This sets up a REACT agent that will handle the overall task execution
agent_executor = create_react_agent(model, tools, checkpointer=memory, debug=False)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Hello! Welcome to SIT Chat bot. How can I assist you?")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):

    chat_id = message.chat.id # Unique chat ID for each user
    config = get_user_config(chat_id)

    # conversation history of user
    messages = config['configurable']['message_history']

    # appending the human's message
    messages.append(HumanMessage(content=message.text))

    response = agent_executor.invoke(
        
        # Including the system prompt and and message entered by the user to be included into the prompt
        {"messages": messages},

        # Indicating the chat conversation history of the user
        config=config
    ) 

    # assigning the result of the output
    result = response["messages"][-1]   

    # checking if the result is an AIMessage, to be printed by the UI   
    if isinstance(result, AIMessage):

        print(f"User: {config['configurable']['thread_id']} \n query: {message.text} \n answer: {result.content} \n length of convo: {len(config['configurable']['message_history'])}")

        # creating a model that returns an emotions
        sticker_response = model.invoke([HumanMessage(content=sticker_prompt(result.content))])

        # printing the result through telegram
        bot.send_message(message.chat.id, result.content, reply_to_message_id=message.message_id )

        # printing the sticker through telegra
        emoji_printer(sticker_response.content, chat_id)

        # appending the result
        messages.append(AIMessage(content=result.content))
    
    # Summmary function implementation
    summary_runnable = RunnableLambda(summary_fn)
    messages = summary_runnable.invoke(messages)

    # storing the messages back into the config
    config['configurable']['message_history'] = messages
        
bot.infinity_polling()
