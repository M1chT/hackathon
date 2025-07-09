from mcp.server.fastmcp import FastMCP
from langchain_tavily import TavilySearch

import warnings
# Suppress SyntaxWarnings for invalid escape sequences
warnings.filterwarnings("ignore", category=SyntaxWarning)

import os
from dotenv import load_dotenv

load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

mcp = FastMCP("Math")

@mcp.tool()
async def search(query: str, num_results: int=3) -> dict:
    """
    Perform a web search using the TavilySearch tool.

    Args:
        query (str): The search query string to look up on the web.
        num_results (int, optional): The maximum number of search results to return. Defaults to 3.

    Returns:
        dict: A dictionary containing the top search results, including titles, links, and snippets.
    """
    search_tool = TavilySearch(max_results=num_results)
    results = await search_tool.ainvoke(query)
    return results

if __name__ == "__main__":
    mcp.run(transport="stdio")