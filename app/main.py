from fastapi import FastAPI, APIRouter
from app.schemas import State
from app.orchestrator import chatbot_pipeline
from langgraph.types import Command

app = FastAPI(title="MCP Claim System")
router = APIRouter()


@router.post("/")
async def send_query(input_query: State):
    graph = await chatbot_pipeline()
    # TO REPLACE: frontend/client to generate and send a session_id (or thread_id)
    config = {"configurable": {"thread_id": "1"}}
    
    state = input_query

    printed_count = 0  # Track how many messages have been shown

    while True:

        results = await graph.ainvoke(state, config)
        messages = results.get("messages", [])

        # Print new messages only (including those leading up to interrupt)
        new_messages = messages[printed_count:]
        for msg in new_messages:
            msg.pretty_print()
        printed_count = len(messages)
        
        # if state['messages'].contains("accept") or state['messages'].contains("reject"):
        #     type = state['messages']
            


        if "__interrupt__" in results:
            # Handle interrupt, keep printed_count so we don't reprint messages post-resume
            state = Command(resume=[{"type": "accept"}])  # or "accept" if simulating user confirmation
            continue
        else:
            return messages[-1]



app.include_router(router, prefix="/send_query")