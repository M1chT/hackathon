from fastapi import FastAPI, APIRouter
from app.schemas import State
from app.orchestrator import chatbot_pipeline
from langgraph.types import Command
from langchain_core.messages import AIMessage
import re

app = FastAPI(title="MCP Claim System")
router = APIRouter()


@router.post("/")
async def send_query(input_query: State):
    graph = await chatbot_pipeline()
    # TO REPLACE: frontend/client to generate and send a session_id (or thread_id)
    config = {"configurable": {"thread_id": "1"}}
    
    state = input_query

    printed_count = 0  # Track how many messages have been shown
    tool_names = []
    while True:

        results = await graph.ainvoke(state, config)
        messages = results.get("messages", [])


        for msg in reversed(messages):
            if isinstance(msg, AIMessage):
                tool_calls = msg.additional_kwargs.get("tool_calls", None)
                if tool_calls:
                    tool_names = [call['function']['name'] for call in tool_calls]
                    break

 
        if "tools to be used:" in state['messages']:
            match = re.search(r"tools to be used:(accept|reject)\b", state['messages'])
            matched_str = match.group(0)
            action = matched_str.split(":")[1]

            state = Command(resume=[{"type": action}])  # Auto-resume
     
        if "__interrupt__" in results:
            tools_str = ", ".join(tool_names) if tool_names else "external tools"
            return {
                "content": f"This action will trigger the use of the following tools: `{tools_str}`. "
                        f"Do you want to proceed?\n\n"
                        f"Please reply with `'tools to be used:accept'` to continue or `'tools to be used:reject'` to cancel."
            }

        else:
            tools_str = ", ".join(tool_names) if tool_names else None
            last_message = messages[-1]
            final_content = last_message.content

            if tools_str:
                final_content += f"\n\n🔧 Tool(s) used: {tools_str}"
                
            return {"content": final_content}
        

app.include_router(router, prefix="/send_query")