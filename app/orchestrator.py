from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import ToolMessage, SystemMessage, HumanMessage

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from mcp_server.tools.infographics_tool import generate_infographics_tool

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


def infographic_generation(state: State):
    """
    Generate an infographic for the internal launch of a digital tool.

    Args:
        query (str): The user query containing product name, description, unique selling point, recommended style, and tagline.

    Returns:
        dict: A dictionary containing the generated infographic details.
    """
    response = generate_infographics_tool(state['messages'][-1].content)
    print(response)
    return response

# Define the conditional edge that determines whether to continue or not
def decision_criteria(state: State):
    messages = state["messages"]

    decision_model = init_chat_model("gpt-4o")  

    prompt = [
        SystemMessage(content="If the query's intent is to generate an infographic, respond with 'infographic'. Otherwise, respond with 'end'." \
        "Only respond with the exact word: either 'infographic' or 'end', and nothing else."),
        HumanMessage(content=f"{messages}")
    ]

    response = decision_model.invoke(prompt)

    # If the last message is a tool call, then we call the tool
    if messages[-1].tool_calls:
        return "call tool"
    elif response.content == "infographic":
        return "infographics"
    else:
        return "end"



async def chatbot_pipeline():
    graph_builder = StateGraph(State)
    graph_builder.add_node("llm", call_model)
    graph_builder.add_node("tools", call_tool)
    graph_builder.add_node("infographics", infographic_generation)

    graph_builder.add_edge(START, "llm")
    graph_builder.add_conditional_edges(
        "llm",
        decision_criteria,
        {
            # If `tool`, then we call the tool node.
            "call tool": "tools",
            # if `generate infographircs` we infographics.
            "infographics": "infographics",
            # If `end`, then we end the graph.
            "end": END,
        },
    )
    graph_builder.add_edge("tools", "llm")
    graph_builder.add_edge("infographics", END)

    graph = graph_builder.compile(checkpointer=checkpointer)
    return graph