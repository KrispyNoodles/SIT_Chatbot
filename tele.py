import telebot
from dotenv import dotenv_values
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.checkpoint.memory import MemorySaver
from langchain.document_loaders import PyPDFLoader
from langchain.tools.retriever import create_retriever_tool
from langgraph.prebuilt import create_react_agent
import uuid
import pandas as pd
import redis
from langchain_redis import RedisVectorStore

# retrieving the env file
env_vars = dotenv_values(".env")

# retrieving the API key
tele_key=env_vars["API_KEY_TELE"]
bot = telebot.TeleBot(tele_key,parse_mode=None)

r = redis.Redis(
  host='redis-19030.c1.ap-southeast-1-1.ec2.redns.redis-cloud.com',
  port=19030,
  password=env_vars["REDIS_PW"])

# declaring the model and using the variables from the env file
model = ChatOpenAI(
    api_key=env_vars["OPENAI_API_KEY"],
)

# entering the creditials
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=env_vars["OPENAI_API_KEY"],
)

REDIS_URL = env_vars["REDIS_URL"]

# retrieved yaml schema from Redis
schema_yaml_from_redis = r.get("vector_store_schema")
schema_yaml_str = schema_yaml_from_redis.decode("utf-8")

with open("retrieved_vector_store_schema.yaml", "w") as f:
        f.write(schema_yaml_str)

new_vector_store = RedisVectorStore(
    embeddings,
    redis_url=REDIS_URL,
    schema_path="retrieved_vector_store_schema.yaml"
)

# a retriever which is used to find and return relevant text chunks based onf a query
retriever = new_vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})

# Initialising a memory which is used to save and retrieve conversation state to enable
# continuity in the chatbot's interactions
memory = MemorySaver()

# building a retriever tool
tool =create_retriever_tool(
    retriever, # retriever that was set up previously
    "SIT_handbook_retriever", # the name of the tool
    "searches and returns excerpts from the SIT student handbook."
)

# A list that holds all the tools that the agent can use
tools = [tool]

# This sets up a REACT agent that will handle the overall task execution
agent_executor = create_react_agent(model, tools, checkpointer=memory)

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


@bot.message_handler(func=lambda message: True)  # This listens to all messages
def handle_all_messages(message):

    chat_id = message.chat.id # Unique chat ID for each user
    config = get_user_config(chat_id)

    # Defining a prompt for the system
    system_prompt = (
        "I am an assistant that specializes in answering questions for SIT (Singapore Institute of Technology)"
        "Use the provided handbook context to answer the questions. If you don't know the answer, say so. "
        "Keep your answers concise and informative.\n\n"
        "At the end of each reply, always append one description in square brackets that best summarizes the tone or content of the reply."
        "Choose only from the following square bracket words: [smiling_eyes], [victory_hands], [perfect], [graduation], [happy], [smiling], [neutral], [curious], [informative], [descriptive]."
    )

    response = agent_executor.invoke(
        
        # Including the system prompt and and message entered by the user to be included into the prompt
        {"messages": [AIMessage(system_prompt), HumanMessage(content=message.text)]},

        # Indicating the chat conversation history of the user
        config=config
    )  

    # assigning the result of the output
    result = response["messages"][-1]   

    # checking if the result is an AIMessage, to be printed by the UI   
    if isinstance(result, AIMessage):

        print(f"User: {config} \n query: {message.text} \n answer: {result.content}")

        # if the chatbot wants to send a sticker
        result_clean = emoji_printer(result.content, chat_id)

        # printing the result through telegram
        bot.send_message(message.chat.id, result_clean, reply_to_message_id=message.message_id )    
        
bot.infinity_polling()