import uuid
import pandas as pd
from config import bot
from prompts import tele_system_prompt
from langchain_core.messages import SystemMessage

# a function to create a new id for different users
user_configs = {}

def get_user_config(chat_id):

    # If the user already has a config, return it
    if chat_id in user_configs:
        return user_configs[chat_id]
    
    # Otherwise, generate a new unique config_no using uuid
    config_no = str(uuid.uuid4())  # Generate a unique identifier for each user (config_no)
    
    # creating a nested dictionary with a key called "thread_id"
    config = {"configurable": {"thread_id": config_no, "message_history": [SystemMessage(content=tele_system_prompt)]}}
    user_configs[chat_id] = config
    
    return config

# Define the sticker data for the DataFrame
sticker_data = [
    ["smiling_eyes", "CAACAgUAAxkBAAPTZxERmzkhktIF2O8H7iHq06b9lg8AApQQAALQC3BUHqFtb71xq3E2BA"],
    ["victory_hands", "CAACAgUAAxUAAWcRFZfDSEM9UsX1Iai5ndRrs6Y0AAILEgAC9pBwVGNiRxMDr4OXNgQ"],
    ["perfect", "CAACAgUAAxUAAWcRFZdPy-CMFIfmiMGpt6MPpDZiAALGEwACaIFoVMH08zfYF9hlNgQ"],
    ["graduation", "CAACAgUAAxUAAWcRFZeJKz3ypli7CWqlAsgLYPBnAALAFAACWhhpVGot5ijZx4N9NgQ"],
    ["happy", "CAACAgUAAxkBAAPeZxER3InyvvcdCEkVdyi6JURUuAEAAvwRAAJnrnFU8BsKAhtiOs02BA"],
    ["smiling", "CAACAgUAAxUAAWcRFZfstb1jhINewQhrRQjmD-BeAALfGAACHRZwVKFXHp66RoL1NgQ"]
]

# Create the DataFrame
emoji_df = pd.DataFrame(sticker_data, columns=["Description", "File ID"])

# using a try if in case the chatbot forgets to include the square brackets
def emoji_printer(sticker_response, chat_id):
    
    try:
        sticker_response = sticker_response.strip("[]").lower()

        # Check if the description exists in the DataFrame and retrieve the File ID
        if sticker_response in emoji_df["Description"].tolist():

            # retrieving the file_id from the dataframe
            file_id = emoji_df.loc[emoji_df["Description"] == sticker_response, "File ID"].values[0]

            # sending the sticker
            bot.send_sticker(chat_id=chat_id, sticker=file_id)
            print("emoji sent")

        else:
            print(f"No emoji sent")

    except IndexError:
        print("No valid description in the AI reply.")


from prompts import system_prompt, summary_prompt
from config import mini_model
from langchain_core.messages import SystemMessage

def summary_fn(messages):
    
    # length of conversation before the function is used
    summary_len = 6

    if len(messages)>=summary_len:

        summary_prompter = SystemMessage(content=summary_prompt)
        
        # replacing previous system prompt with summary system prompt
        messages[0] = summary_prompter
        
        # creating a summary from the llm
        summary = mini_model.invoke(messages)
        
        print(f"summary_function called, summary is: {summary.content}")
        
        # clearing the history and creating a new chat history, appending the summary
        messages = [SystemMessage(content=system_prompt)]
        messages.append(summary)
    
        return messages
    
    else:
        return messages

# creating buttons for the chatbot
import chainlit as cl
def generate_actions(suggestions):
    """Generate exactly 2 action buttons dynamically."""
    return [
        cl.Action(name="action_button_1", value=suggestions[0], label=suggestions[0]),
        cl.Action(name="action_button_2", value=suggestions[1], label=suggestions[1]),
    ]
