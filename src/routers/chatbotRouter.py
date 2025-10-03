from fastapi import APIRouter
from pydantic import BaseModel

from src.agents.guardAgent import agent as guardAgent

# Create an APIRouter instance
router = APIRouter()

@router.get("/")
async def read_all_items():
    return "hello world"


@router.get("/test")
async def get_conversation(item_id: int = 10, q: str | None = None):
    return {"test": item_id, "q": q}



class ChatRequest(BaseModel):
    query: str

@router.post("/chat")
async def create_message(request: ChatRequest):
    """
    Invokes the Guard Agent with the user's query and returns the response.
    """

    response = await guardAgent.run(request.query)

    # Outputting the final response from the agent
    return {
        "query": request.query,
        "response": response
    }