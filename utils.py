import uuid
import pandas as pd
from config import bot

# a function to create a new id for different users
user_configs = {}

def get_user_config(chat_id):

    # If the user already has a config, return it
    if chat_id in user_configs:
        return user_configs[chat_id]
    
    # Otherwise, generate a new unique config_no using uuid
    config_no = str(uuid.uuid4())  # Generate a unique identifier for each user (config_no)
    
    # creating a nested dictionary with a key called "thread_id"
    config = {"configurable": {"thread_id": config_no}}
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
def emoji_printer(ai_reply, chat_id):
    output_cleaned = ai_reply  # Initialize this before the if block
    
    try:
        # Extract the description from the output string (remove brackets)
        description_to_find = ai_reply.split('[')[1].split(']')[0]
        print(description_to_find)
        # Check if the description exists in the DataFrame and retrieve the File ID
        if description_to_find in emoji_df["Description"].tolist():

            # retrieving the file_id from the dataframe
            file_id = emoji_df.loc[emoji_df["Description"] == description_to_find, "File ID"].values[0]

            # sending the sticker
            bot.send_sticker(chat_id=chat_id, sticker=file_id)
            print("emoji sent")
            
            # Remove the description and brackets from the output string
            output_cleaned = ai_reply.replace(f"[{description_to_find}]", "").strip()

        else:
            print(f"No emoji sent")

            # Remove the description and brackets from the output string if neutral is added
            output_cleaned = ai_reply.replace(f"[{description_to_find}]", "").strip()
    
    except IndexError:
        print("No valid description in the AI reply.")
        
    return output_cleaned
