from typing import List, Dict, Optional
from datetime import datetime
from src.db.mongodb import mongodb
from src.utils.constants import RECENT_MESSAGES_THRESHOLD, SUMMARIZATION_THRESHOLD
from pydantic import BaseModel


class ConversationMessage(BaseModel):
    """Schema for a single message in conversation history."""
    role: str  # "user" or "agent"
    content: str
    timestamp: datetime
    metadata: Optional[Dict] = None


class ConversationService:
    """
    Handles conversation history storage and retrieval from MongoDB.
    """

    @staticmethod
    async def get_conversation_history(conversation_id: str) -> List[Dict]:
        """
        Retrieve conversation history from MongoDB.
        Applies smart summarization if conversation exceeds threshold.

        Args:
            conversation_id: Unique conversation identifier

        Returns:
            List of message dictionaries in Pydantic AI format
            Returns empty list if conversation not found
        """
        collection = mongodb.conversations

        conversation = await collection.find_one(
            {"conversationId": conversation_id}
        )

        if not conversation or not conversation.get("messages"):
            print(f"[ConversationService] No history found for: {conversation_id}")
            return []

        messages = conversation["messages"]
        total_messages = len(messages)
        print(f"[ConversationService] Retrieved {total_messages} messages for: {conversation_id}")

        # If conversation is short, return all messages (no summarization)
        if total_messages <= SUMMARIZATION_THRESHOLD:
            print(f"[ConversationService] Conversation below threshold ({total_messages} <= {SUMMARIZATION_THRESHOLD}), returning full history")
            return ConversationService._convert_to_pydantic_format(messages)

        # Otherwise, summarize old messages + keep recent ones full
        print(f"[ConversationService] Conversation exceeds threshold, applying smart summarization")
        return await ConversationService._get_summarized_history(messages)

    @staticmethod
    def _convert_to_pydantic_format(messages: List[Dict]) -> List[Dict]:
        """
        Convert MongoDB message format to Pydantic AI message format.

        Pydantic AI expects:
        - role: "user" or "model" (not "agent")
        - parts: [{"text": "..."}] or just text content depending on model
        """
        pydantic_messages = []

        for msg in messages:
            role = msg["role"]
            # Convert "agent" to "model" for Pydantic AI compatibility
            if role == "agent":
                role = "model"

            pydantic_messages.append({
                "role": role,
                "content": msg["content"]
            })

        return pydantic_messages

    @staticmethod
    async def save_message_pair(
        conversation_id: str,
        user_message: str,
        agent_response: str,
        agent_metadata: Optional[Dict] = None
    ):
        """
        Save user message and agent response to conversation history.
        Creates new conversation document if it doesn't exist.

        Args:
            conversation_id: Unique conversation identifier
            user_message: User's message text
            agent_response: Agent's response text
            agent_metadata: Optional metadata about agent's response (tool calls, model, etc.)
        """
        collection = mongodb.conversations
        now = datetime.now()

        user_msg = {
            "role": "user",
            "content": user_message,
            "timestamp": now
        }

        agent_msg = {
            "role": "agent",
            "content": agent_response,
            "timestamp": now,
            "metadata": agent_metadata or {}
        }

        # Upsert: update if exists, create if doesn't
        result = await collection.update_one(
            {"conversationId": conversation_id},
            {
                "$push": {
                    "messages": {
                        "$each": [user_msg, agent_msg]
                    }
                },
                "$set": {
                    "updatedAt": now
                },
                "$setOnInsert": {
                    "createdAt": now
                }
            },
            upsert=True
        )

        if result.upserted_id:
            print(f"[ConversationService] Created new conversation: {conversation_id}")
        else:
            print(f"[ConversationService] Updated conversation: {conversation_id}")

    @staticmethod
    async def delete_conversation(conversation_id: str):
        """Delete a conversation and its history."""
        collection = mongodb.conversations
        result = await collection.delete_one({"conversationId": conversation_id})
        print(f"[ConversationService] Deleted conversation: {conversation_id} (deleted: {result.deleted_count})")

    @staticmethod
    async def _get_summarized_history(messages: List[Dict]) -> List[Dict]:
        """
        Create hybrid history: summary of old messages + full recent messages.

        Args:
            messages: All messages from conversation

        Returns:
            List with summary message + recent full messages in Pydantic AI format
        """
        from src.agents.summarizationAgent import summarize_messages

        # Split into old and recent
        messages_to_summarize = messages[:-RECENT_MESSAGES_THRESHOLD]
        recent_messages = messages[-RECENT_MESSAGES_THRESHOLD:]

        print(f"[ConversationService] Summarizing {len(messages_to_summarize)} old messages, keeping {len(recent_messages)} recent")

        # Get summary of old messages
        summary_result = await summarize_messages(messages_to_summarize)

        # Create synthetic "system" message with summary
        summary_message = {
            "role": "system",
            "content": f"""Previous conversation context (summarized):

            {summary_result.summary}

            Key entities mentioned: {', '.join(summary_result.key_entities)}
            User intent: {summary_result.user_intent}

            [Recent conversation continues below...]"""
        }

        # Convert recent messages to Pydantic format
        recent_pydantic = ConversationService._convert_to_pydantic_format(recent_messages)

        # Return: [Summary] + [Recent messages]
        return [summary_message] + recent_pydantic
