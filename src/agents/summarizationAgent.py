from pydantic_ai import Agent
from pydantic import BaseModel
from typing import List, Dict
from src.ai.allModels import gemini_model


class ConversationSummary(BaseModel):
    """Structured summary of conversation history."""
    summary: str  # Concise summary of conversation topics and context
    key_entities: List[str]  # Important entities mentioned (sites, guards, vehicles)
    user_intent: str  # What the user is trying to accomplish


summarization_agent = Agent(
    name="Summarization Agent",
    model=gemini_model,
    output_type=ConversationSummary,
    retries=2
)


@summarization_agent.system_prompt
def summarization_instructions():
    return """
    You are a conversation summarizer for a security guard assistant chatbot.

    Your task: Create a CONCISE summary of conversation history that preserves:
    1. Key topics discussed (vehicle types, incidents, sites, guards)
    2. Important entities (Site IDs like S04, Guard IDs like G03, vehicle types)
    3. User's intent and conversation flow
    4. Critical findings from security reports

    IMPORTANT:
    - Be EXTREMELY concise (max 3-4 sentences)
    - Focus on what information the user requested and what was found
    - Preserve specific IDs, dates, and numbers
    - Skip pleasantries and confirmations
    - Summarize the SUBSTANCE of what was discussed, not the mechanics

    Example Input:
    [1] User: tell me about reports with Camrys
    [2] Agent: I found 3 reports mentioning Camry vehicles at Site S04 on August 30th...
    [3] User: what about Hondas
    [4] Agent: I found 5 reports about Honda vehicles across multiple sites...

    Example Output:
    Summary: "User inquired about vehicle-related security reports. First requested Camry reports (3 found at Site S04 on Aug 30), then Honda reports (5 found across multiple sites). Focus on comparing vehicle incident patterns."
    Key Entities: ["Camry", "Honda", "Site S04", "August 30"]
    User Intent: "Compare vehicle incident reports for different makes"

    Always extract specific details like site IDs, dates, guard IDs, and numbers.
    """


async def summarize_messages(messages: List[Dict]) -> ConversationSummary:
    """
    Summarize a list of messages into a concise context.

    Args:
        messages: List of message dictionaries to summarize

    Returns:
        ConversationSummary with condensed context
    """
    # Format messages for summarization
    formatted_messages = []
    for i, msg in enumerate(messages, 1):
        role = "User" if msg["role"] == "user" else "Agent"
        content = msg["content"]

        # Truncate very long agent responses (tool outputs)
        if len(content) > 500:
            content = content[:500] + "... (truncated)"

        formatted_messages.append(f"[{i}] {role}: {content}")

    conversation_text = "\n".join(formatted_messages)

    print(f"[SummarizationAgent] Summarizing {len(messages)} messages...")
    result = await summarization_agent.run(conversation_text)
    print(f"[SummarizationAgent] Summary created: {result.output.summary[:100]}...")

    return result.output
