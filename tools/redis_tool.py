from langchain.tools.retriever import create_retriever_tool
from redis_db import vector_store

# a retriever which is used to find and return relevant text chunks based onf a query
retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 5})

# building a retriever tool
redis_tool = create_retriever_tool(
    retriever,
    "SIT_database",
    "Searches and returns excerpts from the SIT database"
)
