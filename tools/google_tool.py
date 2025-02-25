from langchain_core.tools import Tool
from config import search

google_tool = Tool(
    "Google_Search_Snippets",
    "Search Google for recent results.",
    func=search.run
)