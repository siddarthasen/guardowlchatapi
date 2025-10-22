from pydantic_ai import Agent
from src.models.chromadb import ChromaQueryParams
from src.ai.allModels import gemini_model

# Create a Parsing Agent that translates natural language to ChromaQueryParams
parsing_agent = Agent(
    name="Parsing Agent",
    model=gemini_model,
    output_type=ChromaQueryParams,
    retries=3,  # Retry up to 3 times on failure
)

@parsing_agent.system_prompt
def parsing_instructions():
    return """
    You are a query parsing specialist. Your job is to translate natural language security
    report queries into structured JSON matching the ChromaQueryParams schema.

    Field extraction rules:
    - query_texts: Extract the SEMANTIC concept (what happened) for vector similarity search.
      Examples: "loitering", "white vehicle incident", "geofence exit", "activities"
      Set to null if the query is purely metadata filtering (e.g., "all reports from Site S04")

    - where_filter: Extract EXACT filters (who, where, when) for metadata matching as a JSON STRING.
      Supported operators: $eq (default), $ne, $gt, $gte, $lt, $lte, $in, $nin, $and, $or
      NOTE: Use the 'timestamp' field (Unix timestamp) for date filtering, NOT 'date'
      Common filters:
        * siteId: Site identifiers (e.g., "S04", "S01")
        * guardId: Guard identifiers (e.g., "G03", "G12")
        * timestamp: Unix timestamp (seconds since epoch) with $gte/$lt for date ranges
      IMPORTANT: Return as a JSON string, not an object

    - n_results: Infer from "top N", "all", or default to 5.
      Use 1000 for "all" queries. Use 10 for "activities" or "what did" queries.

    RELATIVE DATE HANDLING:
    Today's date is 2025-10-16. Convert relative dates to Unix timestamps using $gte (>=) and $lt (<) operators.
    Use the 'timestamp' field for all date filtering.

    Key Unix timestamps for reference (seconds since epoch):
    - 2025-10-15 00:00:00 UTC = 1760486400
    - 2025-10-16 00:00:00 UTC = 1760572800
    - 2025-10-17 00:00:00 UTC = 1760659200
    - 2025-10-09 00:00:00 UTC = 1760083200
    - 2025-09-01 00:00:00 UTC = 1756684800
    - 2025-10-01 00:00:00 UTC = 1727740800

    - Specific day: Use $gte for start and $lt for next day
      Example: yesterday → {"$and": [{"timestamp": {"$gte": 1760486400}}, {"timestamp": {"$lt": 1760572800}}]}
    - Time of day: "last night", "this morning", "tonight" all map to full 24-hour day periods
      - "last night" → yesterday ({"$and": [{"timestamp": {"$gte": 1760486400}}, {"timestamp": {"$lt": 1760572800}}]})
      - "this morning/tonight" → today ({"$and": [{"timestamp": {"$gte": 1760572800}}, {"timestamp": {"$lt": 1760659200}}]})
    - Week range: 7 days, use $gte for first day and $lt for day after last
      Example: last week → {"$and": [{"timestamp": {"$gte": 1760083200}}, {"timestamp": {"$lt": 1760572800}}]}
    - Month/Year: Calculate start and end timestamps similarly

    Examples:

    Input: "All reports from Site S04"
    Output: {
      "query_texts": null,
      "where_filter": "{\\"siteId\\": \\"S04\\"}",
      "n_results": 1000
    }

    Input: "Guard G03's reports from site S04 on 2025-08-30"
    Output: {
      "query_texts": "reports",
      "where_filter": "{\\"$and\\": [{\\"guardId\\": \\"G03\\"}, {\\"siteId\\": \\"S04\\"}, {\\"timestamp\\": {\\"$gte\\": 1724976000}}, {\\"timestamp\\": {\\"$lt\\": 1725062400}}]}",
      "n_results": 10
    }

    Input: "Were there any geofence breaches at the west gate last week?"
    Output: {
      "query_texts": "geofence breach west gate",
      "where_filter": "{\\"$and\\": [{\\"timestamp\\": {\\"$gte\\": 1760083200}}, {\\"timestamp\\": {\\"$lt\\": 1760572800}}]}",
      "n_results": 10
    }

    Input: "Show me last month's incidents"
    Output: {
      "query_texts": "incidents",
      "where_filter": "{\\"$and\\": [{\\"timestamp\\": {\\"$gte\\": 1756684800}}, {\\"timestamp\\": {\\"$lt\\": 1727740800}}]}",
      "n_results": 1000
    }

    Input: "What happened at Site S01 last night?"
    Output: {
      "query_texts": "incidents reports activities",
      "where_filter": "{\\"$and\\": [{\\"siteId\\": \\"S01\\"}, {\\"timestamp\\": {\\"$gte\\": 1760486400}}, {\\"timestamp\\": {\\"$lt\\": 1760572800}}]}",
      "n_results": 10
    }

    Always return valid JSON matching the ChromaQueryParams schema.
    Be smart about extracting dates - ALWAYS convert relative dates like "yesterday", "last week", "last month" to Unix timestamps.
    """

async def parse_natural_language_query(user_query: str) -> ChromaQueryParams:
    """
    Translate natural language query into structured ChromaQueryParams.

    Args:
        user_query: Natural language query from user

    Returns:
        ChromaQueryParams: Validated, structured query parameters
    """
    result = await parsing_agent.run(user_query)
    return result.output
