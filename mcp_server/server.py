from mcp.server.fastmcp import FastMCP
from mcp_server.tools.search_best_prac import search_best_practices_tool
from mcp_server.tools.infographics_tool import generate_infographics_tool
from mcp_server.tools.telegram_announcement import gen_telegram_announcement_tool
import logging
from langchain_tavily import TavilySearch
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)
# Step 1: Create the MCP server instance
mcp = FastMCP("marketing-chatbot", port=3000)


@mcp.tool()
async def vectordb_search(query: str):
    """
    Search for marketing strategies for best practices in the knowledge base
    Args:
        query (str): The search query string to look up on the knowledge base.

    Returns:
        dict: A dictionary containing the top search results, including titles, links, and snippets.
    """
    retreival = search_best_practices_tool()
    results = await retreival.ainvoke(query)
    return results


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
    logger.info("Performing Web Search...")
    search_tool = TavilySearch(max_results=num_results)
    results = await search_tool.ainvoke(query)
    return results


@mcp.tool()
def infographics_tool(query: str):
    """
    Generate an infographic for the internal launch of a digital tool.

    Args:
        query (str): The user query containing product name, description, unique selling point, recommended style, and tagline.

    Returns:
        dict: A dictionary containing the generated infographic details.
    """
    response = generate_infographics_tool(query)
    return response


@mcp.tool()
def telegram_announcement_tool(query: str):
    """Generate a Telegram announcement for a product or event.

    Args:
        query (str): The user query containing product name, description, unique selling point, recommended style, and tagline.

    Returns:
        dict: A dictionary containing the generated infographic details.
    """
    response = gen_telegram_announcement_tool(query)
    return response


mcp.run(transport="streamable-http")