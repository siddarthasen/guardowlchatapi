import chromadb
import json

class SecurityReportDatabase:
    """Handles ChromaDB initialization and data ingestion."""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize ChromaDB client and collection."""
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection_name = "reports_collection"
        
        # Create or get collection
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            print(f"Loaded existing collection: {self.collection_name}")
        except:
            self.collection = self.client.create_collection(name=self.collection_name)
            print(f"Created new collection: {self.collection_name}")
    
    def ingest_data(self, json_file_path: str):
        """
        Read data.json and populate ChromaDB collection.
        
        Args:
            json_file_path: Path to the JSON file containing security reports
        """
        # Read the JSON file
        with open(json_file_path, 'r') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            raise ValueError("Expected JSON file to contain a list of reports")
        
        # Prepare parallel lists for ChromaDB
        ids = []
        documents = []
        metadatas = []
        
        for item in data:
            # Extract required fields
            report_id = str(item.get('id', f"report_{len(ids)}"))
            document_text = item.get('text', '')
            
            # Build metadata dictionary (exclude 'id' and 'text' from metadata)
            metadata = {k: v for k, v in item.items() if k not in ['id', 'text']}
            
            ids.append(report_id)
            documents.append(document_text)
            metadatas.append(metadata)
        
        # Ingest into ChromaDB
        if ids:
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            print(f"Successfully ingested {len(ids)} reports into ChromaDB")
        else:
            print("No reports to ingest")
    
    def get_collection(self):
        """Return the collection object for querying."""
        return self.collection
