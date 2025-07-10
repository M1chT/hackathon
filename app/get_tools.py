from langchain_mcp_adapters.client import MultiServerMCPClient

from app.utils import add_human_in_the_loop

async def get_tools():
    client = MultiServerMCPClient(
        {
            "math": {
                "transport": "streamable_http",
                "url": "http://localhost:3000/mcp/",
            },
        }
    )
    tools = await client.get_tools()
    # Wrap each tool with human-in-the-loop
    return [add_human_in_the_loop(tool) for tool in tools]