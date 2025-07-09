from mcp.server.fastmcp import FastMCP
from mcp_server.tools.search_best_prac import best_practices
from langchain_tavily import TavilySearch

# Step 1: Create the MCP server instance
mcp = FastMCP("marketing-chatbot", port=3000)


@mcp.tool()
def vectordb_search(query: str):
    """
    Search for marketing strategies for best practices in the knowledge base
    Args:
        query (str): The search query string to look up on the knowledge base.

    Returns:
        dict: A dictionary containing the top search results, including titles, links, and snippets.
    """
    retreival = best_practices()
    results = retreival.invoke(query)
    return results

#testing
@mcp.tool()
def add(a: int, b: int) -> int:
    """add two numbers"""
    return a + b


@mcp.tool()
async def search_web(query: str, num_results: int = 3) -> dict:
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


mcp.run(transport="streamable-http")
