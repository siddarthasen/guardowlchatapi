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

# MongoDB Configuration
MONGODB_URI = os.getenv('MONGODB_URI')
MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'guardowl_db')

# Conversation History Summarization
RECENT_MESSAGES_THRESHOLD = 10  # Keep last 10 messages (5 pairs) in full detail
SUMMARIZATION_THRESHOLD = 12    # Only summarize if total messages > 12
MAX_SUMMARY_TOKENS = 500        # Target token count for summary