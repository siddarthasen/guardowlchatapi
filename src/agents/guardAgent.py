from pydantic_ai import Agent, RunContext

from src.ai.allModels import gemini_model

agent = Agent(
    name="Guard Agent", 
    model=gemini_model,
    toolsets=[]
)

@agent.instructions
def guard_instructions():
    return """
    You are an agent that responds to security guards' queries.
    You can provide information about security protocols, emergency procedures, and general safety guidelines.
    Always prioritize the safety and security of individuals and property.
    If you don't know the answer, utillize the tools to answer the question or connect them with support."""


@agent.tool
def call_support(context: RunContext, issue: str) -> str:
    """
    Connect the guard with support for urgent issues. Use this even if the guard only asks for the number.
    """
    # Here you would implement the logic to connect with support.
    return f"Call 111-111-1111 for support regarding: {issue}"


@agent.tool
def provide_shift_schedule(context: RunContext, date: str) -> str:
    """
    Provide the shift schedule for a given date. The date can be a specific date (e.g., '2025-10-03') 
    or a relative date (e.g., 'today', 'tomorrow', 'next week'). The LLM should extract the relevant date string.
    """
    # Here you would implement the logic to retrieve the shift schedule.
    return f"Shift schedule for {date}: 9 AM - 5 PM"