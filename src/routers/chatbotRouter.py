from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from src.agents.guardAgent import agent as guardAgent
from src.services.conversationService import ConversationService

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
    conversationId: Optional[str] = None  # NEW: Optional conversation ID

@router.post("/chat")
async def create_message(request: ChatRequest):
    """
    Invokes the Guard Agent with the user's query and conversation history.
    Stores the conversation in MongoDB after agent responds.
    """

    # Step 1: Retrieve conversation history (if conversationId provided)
    message_history = []
    if request.conversationId:
        message_history = await ConversationService.get_conversation_history(
            request.conversationId
        )

    # Step 2: Run agent with message history
    # Pydantic AI accepts message_history parameter
    if message_history:
        response = await guardAgent.run(
            request.query,
            message_history=message_history
        )
    else:
        response = await guardAgent.run(request.query)

    # Step 3: Extract agent response
    agent_output = response.data if hasattr(response, 'data') else str(response)

    # Step 4: Store conversation in MongoDB
    if request.conversationId:
        # Extract metadata about tool calls if available
        metadata = {
            "model": "gemini-2.0-flash"
        }

        # Check if agent used tools (tool calls stored in response)
        if hasattr(response, 'all_messages'):
            # Extract tool names from messages
            tool_calls = []
            for msg in response.all_messages():
                if hasattr(msg, 'parts'):
                    for part in msg.parts:
                        if hasattr(part, 'tool_name'):
                            tool_calls.append(part.tool_name)

            if tool_calls:
                metadata["toolCalls"] = tool_calls

        await ConversationService.save_message_pair(
            conversation_id=request.conversationId,
            user_message=request.query,
            agent_response=agent_output,
            agent_metadata=metadata
        )

    # Step 5: Return response
    return {
        "query": request.query,
        "response": response,
        "conversationId": request.conversationId
    }


@router.delete("/conversation/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation history."""
    await ConversationService.delete_conversation(conversation_id)
    return {"status": "deleted", "conversationId": conversation_id}