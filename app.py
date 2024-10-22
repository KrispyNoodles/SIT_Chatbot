import chainlit as cl
from dotenv import dotenv_values
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.checkpoint.memory import MemorySaver
from langchain.document_loaders import PyPDFLoader
from langchain.tools.retriever import create_retriever_tool
from langgraph.prebuilt import create_react_agent
import redis
from langchain_redis import RedisVectorStore

# retrieving the env file
env_vars = dotenv_values(".env")

# a potentional function yet to be built that retrieves the "thread_id"
config_no = "abc123"

# creating a nested dictionary with a key called "thread_id"
config = {"configurable": {"thread_id": config_no}}

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
tool = create_retriever_tool(
    retriever, # retriever that was set up previously
    "SIT_database", # the name of the tool
    "Searches and returns excerpts from the SIT database" # description of what the tool does
)

# A list that holds all the tools that the agent can use
tools = [tool]

# This sets up a REACT agent that will handle the overall task execution
agent_executor = create_react_agent(model, tools, checkpointer=memory)

# on_chat_start decorator is used when the chat bot has started
@cl.on_chat_start
async def on_chat_start():
    sentence = "Hello!! Welcome to this chatbot"
    await cl.Message(content=sentence).send()

# Defining a prompt for the system
system_prompt = (
    "I am an assistant that specializes in answering questions for SIT (Singapore Institute of Technology)"
    "Use the provided handbook context to answer the questions. If you don't know the answer, say so. "
    "Keep your answers concise and informative.\n\n"
    "Joey is my creator and he is super cool and smart and unerdy"
)

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
