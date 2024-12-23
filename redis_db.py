from langchain_redis import RedisVectorStore
from config import embeddings, REDIS_URL

vector_store = RedisVectorStore(
    embeddings,
    redis_url=REDIS_URL,
    schema_path="redis_schema.yaml"
)