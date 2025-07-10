from fastapi import FastAPI, APIRouter
from app.schemas import State
from app.orchestrator import chatbot_pipeline
from langgraph.types import Command
from langchain_core.messages import AIMessage
import re

app = FastAPI(title="Promogenie")
router = APIRouter()

@router.post("/")
async def send_query(input_query: State):
    graph = await chatbot_pipeline()
    # TO REPLACE: frontend/client to generate and send a session_id (or thread_id)
    config = {"configurable": {"thread_id": "1"}}
    
    state = input_query
    tool_names = []
    printed_count = 0  # Track how many messages have been shown

    while True:

        results = await graph.ainvoke(state, config)
        messages = results.get("messages", [])
        for msg in reversed(messages):
            if isinstance(msg, AIMessage):
                tool_calls = msg.additional_kwargs.get("tool_calls", None)
                if tool_calls:
                    tool_names = [call['function']['name'] for call in tool_calls]
                    break

        if "__interrupt__" in results:
            state = Command(resume=[{"type": "accept"}])

        else:
            # ✅ Final response after graph finishes
            tools_str = ", ".join(tool_names) if tool_names else None
            last_message = messages[-1]
            final_content = last_message.content if hasattr(last_message, "content") else str(last_message)

            if tools_str:
                final_content += f"\n\n🔧 Tool(s) used: {tools_str}"

            return {"content": final_content}
     
        




# @router.post("/")
# async def send_query(input_query: State):
#     graph = await chatbot_pipeline()
#     # TO REPLACE: frontend/client to generate and send a session_id (or thread_id)
#     config = {"configurable": {"thread_id": "1"}}
    
#     state = input_query
#     tool_names = []
#     while True:

#         results = await graph.ainvoke(state, config)
#         messages = results.get("messages", [])


#         for msg in reversed(messages):
#             if isinstance(msg, AIMessage):
#                 tool_calls = msg.additional_kwargs.get("tool_calls", None)
#                 if tool_calls:
#                     tool_names = [call['function']['name'] for call in tool_calls]
#                     break
#         if "__interrupt__" in results:
#             # Handle interrupt, keep printed_count so we don't reprint messages post-resume
#             state = Command(resume=[{"type": "accept"}])  # or "accept" if simulating user confirmation
#             continue
#         else:
#             last_msg = messages[-1]
#             content = last_msg.content if hasattr(last_msg, "content") else str(last_msg)
#             if tool_names:
#                 content += f"\n\n🔧 Tool(s) used: {', '.join(tool_names)}"
#             return {"content": content}

        #  #  Handle interrupt
        # if "__interrupt__" in results:
        #     # Check if user already replied with accept/reject
        #     for m in results["messages"]:
        #         if isinstance(m, str) and "tools to be used:" in m:
        #             match = re.search(r"tools to be used:(accept|reject)\b", m)
        #             if match:
        #                 action = match.group(1)
        #                 #  RESUME graph with Command
        #                 state = Command(resume=[{"type": action}])
                        
        #     else:
        #         #  No accept/reject yet — prompt user
        #         tools_str = ", ".join(tool_names) if tool_names else "external tools"
        #         return {
        #             "content": f"This action will trigger the use of the following tools: `{tools_str}`. "
        #                        f"Do you want to proceed?\n\n"
        #                        f"Please reply with `'tools to be used:accept'` to continue or `'tools to be used:reject'` to cancel."
        #         }
        # else:
        #     # ✅ Done, return latest message and tool info
        #     last_msg = messages[-1]
        #     content = last_msg.content if hasattr(last_msg, "content") else str(last_msg)
        #     if tool_names:
        #         content += f"\n\n🔧 Tool(s) used: {', '.join(tool_names)}"
        #     return {"content": content}
        

app.include_router(router, prefix="/send_query")