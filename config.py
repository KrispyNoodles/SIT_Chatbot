from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import redis
from dotenv import dotenv_values
from langchain_google_community import GoogleSearchAPIWrapper
import telebot

# retrieving the env file
env_vars = dotenv_values(".env")

tool_usage_log = []

from langchain.callbacks.base import AsyncCallbackHandler
from typing import Any, Optional
from uuid import UUID
from langchain_core.messages import AIMessage
import json

class VerboseCallbackHandler(AsyncCallbackHandler):
    async def on_chat_model_start(
        self,
        serialized: dict[str, Any],
        messages: list[list[Any]],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        
        # Get only the latest message (last element)
        latest_message_group = messages[-1] if messages else []
        
        # Extract tool calls from the latest AIMessage only
        tool_calls = []
        global tool_usage_log
        
        for msg in latest_message_group:
            if isinstance(msg, AIMessage) and "tool_calls" in msg.additional_kwargs:
                tool_calls = msg.additional_kwargs["tool_calls"]  # Only the latest tool call
                                
        # Extract tool name and query if a tool call exists
        if len(tool_calls) > 0:
            tool_name = tool_calls[0]['function']['name']
            arguments = json.loads(tool_calls[0]['function']['arguments'])  # Use json.loads instead of eval

            if 'query' in arguments:
                query = arguments['query']
                output_text = f'The tool being called is "{tool_name}" and the query fed into it is "{query}"'
                tool_usage_log.append(output_text)
                tool_calls.clear()
            
            elif '__arg1' in arguments:  # Checking for Google Search argument
                search = arguments['__arg1']
                output_text = f'The tool being called is "{tool_name}" and the query fed into it is "{search}"'
                tool_usage_log.append(output_text)
                tool_calls.clear()
                
        else:
            tool_usage_log.clear()
            tool_calls.clear()

# declaring the model and using the variables from the env file
model = ChatOpenAI(
    api_key=env_vars["OPENAI_API_KEY"],
    model="gpt-4o",
    callbacks=[VerboseCallbackHandler()],
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
  host='redis-19084.c10.us-east-1-4.ec2.redns.redis-cloud.com',
  port=19084,
  password=env_vars["REDIS_PW"]
)

REDIS_URL = env_vars["REDIS_URL"]

# retrieving the API key
tele_key=env_vars["API_KEY_TELE"]
bot = telebot.TeleBot(tele_key,parse_mode=None)