from langchain_redis import RedisVectorStore
from config import embeddings, r, REDIS_URL

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