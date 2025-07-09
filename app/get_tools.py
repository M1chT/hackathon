from langchain_mcp_adapters.client import MultiServerMCPClient


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
    return tools
