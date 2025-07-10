from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import ToolMessage

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

from app.schemas import State
from app.get_tools import get_tools

from prompt.gen_prompt import system_prompt

from dotenv import load_dotenv
load_dotenv()

checkpointer = InMemorySaver()

# Define our tool node
async def call_tool(state: State):
    outputs = []
    tools = await get_tools()
    tools_by_name = {tool.name: tool for tool in tools}
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


# Node Functionality
async def call_model(state: State):
    # get mcp tools
    tools = await get_tools()
    
    prompt = ChatPromptTemplate.from_messages(
        [("system", system_prompt), ("user", "{input}")]
    )
    response_model = init_chat_model("openai:gpt-4.1-mini").bind_tools(tools)
    chain = prompt | response_model
    response = await chain.ainvoke(state["messages"])
    return {"messages": [response]}


# Define the conditional edge that determines whether to continue or not
def should_continue(state: State):
    messages = state["messages"]
    # If the last message is a tool call, then we call the tool
    if messages[-1].tool_calls:
        return "call tool"
    # else LLM generates response and ends
    return "end"


async def chatbot_pipeline():
    graph_builder = StateGraph(State)
    graph_builder.add_node("llm", call_model)
    graph_builder.add_node("tools", call_tool)

    graph_builder.add_edge(START, "llm")
    graph_builder.add_conditional_edges(
        "llm",
        should_continue,
        {
            # If `tool`, then we call the tool node.
            "call tool": "tools",
            # if `end` we finish.
            "end": END,
        },
    )
    graph_builder.add_edge("tools", "llm")

    graph = graph_builder.compile(checkpointer=checkpointer)
    return graph