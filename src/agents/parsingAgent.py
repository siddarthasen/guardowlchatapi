from pydantic_ai import Agent
from src.models.chromadb import ChromaQueryParams
from src.ai.allModels import gemini_model

# Create a Parsing Agent that translates natural language to ChromaQueryParams
parsing_agent = Agent(
    name="Parsing Agent",
    model=gemini_model,
    output_type=ChromaQueryParams,
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
      Supported operators: $eq (default), $ne, $gt, $gte, $lt, $lte, $in, $nin, $and, $or, $regex
      Common filters:
        * siteId: Site identifiers (e.g., "S04", "S01")
        * guardId: Guard identifiers (e.g., "G03", "G12")
        * date: ISO date strings. Use $regex for date patterns
      IMPORTANT: Return as a JSON string, not an object

    - n_results: Infer from "top N", "all", or default to 5.
      Use 1000 for "all" queries. Use 10 for "activities" or "what did" queries.

    Examples:

    Input: "What did Guard G03 do on August 30th?"
    Output: {
      "query_texts": "activities",
      "where_filter": "{\\"guardId\\": \\"G03\\", \\"date\\": {\\"$regex\\": \\"^2025-08-30\\"}}",
      "n_results": 10
    }

    Input: "All reports from Site S04"
    Output: {
      "query_texts": null,
      "where_filter": "{\\"siteId\\": \\"S04\\"}",
      "n_results": 1000
    }

    Input: "Top 3 white vehicle incidents"
    Output: {
      "query_texts": "white vehicle incident",
      "where_filter": null,
      "n_results": 3
    }

    Input: "Reports about loitering near north gate"
    Output: {
      "query_texts": "loitering north gate",
      "where_filter": null,
      "n_results": 5
    }

    Input: "Guard G03's reports from site S04 on 2025-08-30"
    Output: {
      "query_texts": "reports",
      "where_filter": "{\\"$and\\": [{\\"guardId\\": \\"G03\\"}, {\\"siteId\\": \\"S04\\"}, {\\"date\\": {\\"$regex\\": \\"^2025-08-30\\"}}]}",
      "n_results": 10
    }

    Always return valid JSON matching the ChromaQueryParams schema.
    Be smart about extracting dates - convert relative dates like "yesterday" to actual dates.
    Today's date is 2025-10-16 for reference.
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
