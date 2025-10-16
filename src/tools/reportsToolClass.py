from typing import Dict, Any
import json
from src.models.chromadb import ChromaQueryParams
from src.agents.parsingAgent import parse_natural_language_query


class ReportsTool:
    """
    The retrieve_security_reports tool.
    Encapsulates: Parsing → ChromaDB Query → Result Formatting
    """

    def __init__(self, collection):
        """
        Initialize the Reports Tool.

        Args:
            collection: ChromaDB collection object
        """
        self.collection = collection

    async def execute(self, user_query: str) -> Dict[str, Any]:
        """
        Main entry point called by Guard Agent.

        Workflow:
        1. Parse natural language query using Parsing Agent
        2. Execute ChromaDB query based on parsed parameters
        3. Format and return results

        Args:
            user_query: Natural language query from user

        Returns:
            {
                "success": bool,
                "count": int,
                "message": str,
                "results": List[Dict]
            }
        """
        try:
            # Step A: Call Parsing Agent
            query_params = await parse_natural_language_query(user_query)
            print(f"[ReportsTool] Parsed query parameters: {query_params}")

            # Step B: Execute ChromaDB Query
            results = self._execute_chromadb_query(query_params)

            # Step C: Return formatted results
            return results

        except Exception as e:
            print(f"[ReportsTool] Error in execute: {str(e)}")
            return {
                "success": False,
                "count": 0,
                "message": f"Error processing query: {str(e)}",
                "results": []
            }

    def _execute_chromadb_query(self, params: ChromaQueryParams) -> Dict[str, Any]:
        """
        Execute the appropriate ChromaDB query based on parameters.

        Args:
            params: Structured query parameters from Parsing Agent

        Returns:
            Dictionary containing success status, count, message, and results
        """
        try:
            # Parse where_filter from JSON string if present
            where_filter_dict = None
            if params.where_filter:
                try:
                    where_filter_dict = json.loads(params.where_filter)
                except json.JSONDecodeError as e:
                    print(f"[ReportsTool] Error parsing where_filter JSON: {e}")
                    return {
                        "success": False,
                        "count": 0,
                        "message": f"Invalid where_filter JSON: {str(e)}",
                        "results": []
                    }

            # Case 1: Pure metadata filtering (most efficient)
            if params.query_texts is None and where_filter_dict:
                results = self.collection.get(
                    where=where_filter_dict,
                    limit=params.n_results
                )

                if not results['ids']:
                    return {
                        "success": False,
                        "count": 0,
                        "message": "No reports matching those criteria could be found in the database.",
                        "results": []
                    }

                # Format results
                formatted_results = []
                for i in range(len(results['ids'])):
                    formatted_results.append({
                        "id": results['ids'][i],
                        "text": results['documents'][i],
                        "metadata": results['metadatas'][i]
                    })

                return {
                    "success": True,
                    "count": len(formatted_results),
                    "message": f"Retrieved {len(formatted_results)} reports",
                    "results": formatted_results
                }

            # Case 2: Semantic search (with optional metadata filtering)
            elif params.query_texts:
                results = self.collection.query(
                    query_texts=[params.query_texts],
                    where=where_filter_dict,
                    n_results=params.n_results
                )

                if not results['ids'][0]:
                    return {
                        "success": False,
                        "count": 0,
                        "message": "No reports matching those criteria could be found in the database.",
                        "results": []
                    }

                # Format results
                formatted_results = []
                for i in range(len(results['ids'][0])):
                    formatted_results.append({
                        "id": results['ids'][0][i],
                        "text": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "distance": results['distances'][0][i]
                    })

                return {
                    "success": True,
                    "count": len(formatted_results),
                    "message": f"Retrieved {len(formatted_results)} reports",
                    "results": formatted_results
                }

            # Case 3: Invalid query (no search criteria)
            else:
                return {
                    "success": False,
                    "count": 0,
                    "message": "Query must include either semantic search text or metadata filters.",
                    "results": []
                }

        except Exception as e:
            print(f"[ReportsTool] ChromaDB query error: {str(e)}")
            return {
                "success": False,
                "count": 0,
                "message": f"Error executing query: {str(e)}",
                "results": []
            }
