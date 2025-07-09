
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.prebuilt import ToolNode

import asyncio

import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Create LLM class
llm = ChatGoogleGenerativeAI(
    model= "gemini-2.5-pro",
    temperature=1.0,
    max_retries=2,
    google_api_key=GEMINI_API_KEY,
)

class AgentState(MessagesState):
    """The state of the agent."""
    step_count: int



async def main():
    client = MultiServerMCPClient(
        {
            "search": {
                "command": "python",
                "args": ["search_server.py"],
                "transport": "stdio"
            }
        }
    )
    
    tools = await client.get_tools()
    
    model = llm.bind_tools(tools)
    
    tools_by_name = {tool.name: tool for tool in tools}
    
    # Define our tool node
    async def call_tool(state: AgentState):
        outputs = []
        # Iterate over the tool calls in the last message
        for tool_call in state["messages"][-1].tool_calls:
            # Get the tool by name
            tool_result = await tools_by_name[tool_call["name"]].ainvoke(tool_call["args"])
            outputs.append(
                ToolMessage(
                    content=tool_result,
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": outputs}

    def call_model(state: AgentState, config: RunnableConfig):
        # Invoke the model with the system prompt and the messages
        response = model.invoke(state["messages"], config)
        # We return a list, because this will get added to the existing messages state using the add_messages reducer
        return {"messages": [response]}


    # Define the conditional edge that determines whether to continue or not
    def should_continue(state: AgentState):
        messages = state["messages"]
        # If the last message is a tool call, then we call the tool
        if messages[-1].tool_calls:
            return "call tool"
        # else LLM generates response and ends
        return "end"
    
    # Define a new graph with our state
    workflow = StateGraph(AgentState)

    # 1. Add our nodes 
    workflow.add_node("llm", call_model)
    workflow.add_node("tools", call_tool)
    # workflow.add_node("tools", ToolNode(tools))

    # 2. Set the entrypoint as `agent`, this is the first node called
    workflow.add_edge(START, "llm")

    # 3. Add a conditional edge after the `llm` node is called.
    workflow.add_conditional_edges(
        "llm",
        should_continue,
        {
            # If `tool`, then we call the tool node.
            "call tool": "tools",
            # if `end` we finish.
            "end": END,
        },
    )

    # 4. Add a normal edge after `tools` is called, `llm` node is called next.
    workflow.add_edge("tools", "llm")

    # compile graph
    graph = workflow.compile()
    
    # Create our initial message dictionary
    inputs = {
        "messages": [
            ("user", f"are there tools for performing data science in a secured environment?")
        ],
    }

    # call our graph with streaming to see the steps
    async for state in graph.astream(inputs, stream_mode="values"):
        last_message = state["messages"][-1]
        last_message.pretty_print()

if __name__ == "__main__":
    asyncio.run(main())