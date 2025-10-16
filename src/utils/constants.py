import os
from dotenv import load_dotenv

load_dotenv()

# Gemini Configuration
GEMINI = 'gemini-2.0-flash'
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# ChromaDB Configuration
CHROMA_PERSIST_DIR = os.getenv('CHROMA_PERSIST_DIR', './chroma_db')
CHROMA_COLLECTION_NAME = os.getenv('CHROMA_COLLECTION_NAME', 'reports_collection')
DEFAULT_N_RESULTS = 5
MAX_N_RESULTS = 1000