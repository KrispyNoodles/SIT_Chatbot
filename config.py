from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import redis
from dotenv import dotenv_values
from langchain_google_community import GoogleSearchAPIWrapper
import telebot

# retrieving the env file
env_vars = dotenv_values(".env")

# declaring the model and using the variables from the env file
model = ChatOpenAI(
    api_key=env_vars["OPENAI_API_KEY"],
    model="gpt-4o",
    temperature=0
)

# entering the creditials
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=env_vars["OPENAI_API_KEY"]
)

# entering the creditials of Google seach
search = GoogleSearchAPIWrapper(
    google_cse_id = env_vars["GOOGLE_CSE_ID"],
    google_api_key = env_vars["GOOGLE_API_KEY"]
)

r = redis.Redis(
  host='redis-10327.c84.us-east-1-2.ec2.redns.redis-cloud.com',
  port=10327,
  password=env_vars["REDIS_PW"]
)

REDIS_URL = env_vars["REDIS_URL"]

# retrieving the API key
tele_key=env_vars["API_KEY_TELE"]
bot = telebot.TeleBot(tele_key,parse_mode=None)