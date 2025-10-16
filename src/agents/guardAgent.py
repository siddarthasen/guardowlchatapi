from pydantic_ai import Agent, RunContext
from typing import Dict, Any
import json

from src.ai.allModels import gemini_model

# The Guard Agent will be initialized with the reports_tool_instance
# This will be set up during application startup
reports_tool_instance = None

def set_reports_tool(tool_instance):
    """Set the reports tool instance for the Guard Agent to use."""
    global reports_tool_instance
    reports_tool_instance = tool_instance

agent = Agent(
    name="Guard Agent",
    model=gemini_model,
)

@agent.system_prompt
def guard_instructions():
    return """
    You are an AI assistant for security guards. You help them with:
    1. Retrieving and analyzing security reports from the database
    2. Answering questions about security protocols and procedures
    3. Providing shift schedules
    4. Connecting them with support when needed

    When a user asks about security reports, incidents, guards, sites, or activities,
    you MUST use the retrieve_security_reports tool to fetch the relevant data from the database.

    After retrieving reports, synthesize the results into a clear, conversational summary that
    directly answers the user's question. Be concise but informative.

    Always prioritize the safety and security of individuals and property.
    """

@agent.tool
async def retrieve_security_reports(context: RunContext, user_query: str) -> str:
    """
    Retrieve security reports from the ChromaDB database based on natural language queries.

    This tool handles both semantic search (e.g., "white vehicle incidents") and metadata
    filtering (e.g., "all reports from Site S04" or "Guard G03's activities on August 30th").

    Args:
        user_query: The user's natural language query about security reports

    Returns:
        A formatted string containing the retrieved reports or an error message
    """
    if reports_tool_instance is None:
        return "Error: Reports database is not available. Please contact support."

    try:
        # Call the reports tool
        result = await reports_tool_instance.execute(user_query)

        # If query failed, return the error message
        if not result["success"]:
            return result["message"]

        # Format the results for the agent to synthesize
        formatted_output = f"Found {result['count']} reports:\n\n"

        for i, report in enumerate(result['results'], 1):
            metadata = report['metadata']
            formatted_output += f"{i}. Report {report['id']}\n"
            formatted_output += f"   Site: {metadata.get('siteId', 'N/A')}, "
            formatted_output += f"Guard: {metadata.get('guardId', 'N/A')}, "
            formatted_output += f"Date: {metadata.get('date', 'N/A')}\n"
            formatted_output += f"   {report['text']}\n"

            # Include distance for semantic searches
            if 'distance' in report:
                formatted_output += f"   (Relevance score: {report['distance']:.2f})\n"

            formatted_output += "\n"

        return formatted_output

    except Exception as e:
        return f"Error retrieving reports: {str(e)}"


@agent.tool
def call_support(context: RunContext, issue: str) -> str:
    """
    Connect the guard with support for urgent issues. Use this even if the guard only asks for the number.

    Args:
        issue: Description of the issue requiring support

    Returns:
        Support contact information
    """
    return f"Call 111-111-1111 for support regarding: {issue}"


@agent.tool
def provide_shift_schedule(context: RunContext, date: str) -> str:
    """
    Provide the shift schedule for a given date. The date can be a specific date (e.g., '2025-10-03')
    or a relative date (e.g., 'today', 'tomorrow', 'next week'). The LLM should extract the relevant date string.

    Args:
        date: The date for which to retrieve the shift schedule

    Returns:
        Shift schedule information
    """
    return f"Shift schedule for {date}: 9 AM - 5 PM"
