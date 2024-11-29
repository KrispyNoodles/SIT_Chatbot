from langchain_core.tools import Tool
from config import search

google_tool = Tool(
    name="Google_Search_Snippets",
    description="Search Google for recent results.",
    func=search.run
)