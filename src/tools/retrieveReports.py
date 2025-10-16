from typing import Any, Dict
from src.models.chromadb import ChromaQueryParams

def retrieve_security_reports(
    collection,
    query_params: ChromaQueryParams
) -> Dict[str, Any]:
    """
    Execute the ChromaDB query based on structured parameters.
    
    Args:
        collection: ChromaDB collection object
        query_params: Structured query parameters
        
    Returns:
        Dictionary containing results or error message
    """
    try:
        # Case 1: Pure metadata filtering (no semantic search)
        if query_params.query_texts is None and query_params.where_filter:
            results = collection.get(
                where=query_params.where_filter,
                limit=query_params.n_results
            )
            
            if not results['ids']:
                return {
                    "success": False,
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
                "results": formatted_results
            }
        
        # Case 2: Semantic search (with optional metadata filtering)
        elif query_params.query_texts:
            results = collection.query(
                query_texts=[query_params.query_texts],
                where=query_params.where_filter,
                n_results=query_params.n_results
            )
            
            if not results['ids'][0]:
                return {
                    "success": False,
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
                "results": formatted_results
            }
        
        # Case 3: Invalid query (no search criteria)
        else:
            return {
                "success": False,
                "message": "Query must include either semantic search text or metadata filters.",
                "results": []
            }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Error executing query: {str(e)}",
            "results": []
        }