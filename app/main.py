from fastapi import FastAPI, APIRouter
from app.schemas import State
from app.orchestrator import chatbot_pipeline

app = FastAPI(title="MCP Claim System")
router = APIRouter()


@router.post("/")
async def send_query(input_query: State):
    config={"configurable":{"thread_id":"user_123"}}
    graph = await chatbot_pipeline()
    result = await graph.ainvoke(input_query, config=config)
    print(result)
    return result
    # async for state in graph.astream(input_query, stream_mode="values"):
    #     last_message = state["messages"][-1]
    # #     last_message.pretty_print()
        
    #     return last_message


app.include_router(router, prefix="/send_query")
