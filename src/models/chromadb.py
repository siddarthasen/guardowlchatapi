import json
import chromadb
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class ChromaQueryParams(BaseModel):
    """
    Structured query parameters for the ChromaDB reports collection.
    The parsing agent must translate the user's query into this schema.
    """
    query_texts: Optional[str] = Field(
        None,
        description=(
            "The core text or incident description for semantic similarity search "
            "(e.g., 'loitering near north gate' or 'geofence exit'). "
            "If the user query is purely a filter (e.g., 'all reports from S04'), "
            "this can be None."
        )
    )
    
    where_filter: Optional[str] = Field(
        None,
        description=(
            "A JSON string representing the ChromaDB 'where' filter applied to document metadata. "
            "Use this for exact match filtering on fields like 'siteId', 'guardId', "
            "or time-based range queries on 'date' using $gte and $lt operators. "
            "Examples: '{\"siteId\": \"S04\"}' or '{\"$and\": [{\"guardId\": \"G03\"}, {\"date\": {\"$gte\": \"2025-08-30\"}}, {\"date\": {\"$lt\": \"2025-08-31\"}}]}'"
        )
    )
    
    n_results: int = Field(
        5,
        description=(
            "The maximum number of results to return. Default is 5. "
            "If the user asks for 'all' or 'everything', choose a large, "
            "safe number (e.g., 1000)."
        )
    )
