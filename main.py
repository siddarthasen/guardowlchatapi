# main.py

from fastapi import FastAPI
from contextlib import asynccontextmanager
import logfire

from src.routers import chatbotRouter
from src.collections.chromadb import SecurityReportDatabase
from src.tools.reportsToolClass import ReportsTool
from src.agents.guardAgent import set_reports_tool
from src.utils.constants import CHROMA_PERSIST_DIR
from src.db.mongodb import mongodb  # NEW: Import MongoDB manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager - runs on startup and shutdown.
    Initializes MongoDB Atlas and ChromaDB, ingests data if collection is empty.
    """
    print("[Startup] Starting application...")

    # Initialize MongoDB connection
    print("[Startup] Connecting to MongoDB Atlas...")
    await mongodb.connect()

    print("[Startup] Initializing ChromaDB...")

    # Initialize ChromaDB
    db = SecurityReportDatabase(persist_directory=CHROMA_PERSIST_DIR)
    collection = db.get_collection()

    # Check if collection is empty and ingest data if needed
    try:
        count = collection.count()
        print(f"[Startup] ChromaDB collection has {count} documents")

        if count == 0:
            print("[Startup] Collection is empty. Ingesting data from src/collections/data.json...")
            db.ingest_data("src/collections/data.json")
            print(f"[Startup] Data ingestion complete. Collection now has {collection.count()} documents")
        else:
            print("[Startup] Collection already populated. Skipping data ingestion.")
    except Exception as e:
        print(f"[Startup] Error during ChromaDB initialization: {str(e)}")
        raise

    # Initialize Reports Tool with the collection
    reports_tool = ReportsTool(collection=collection)

    # Set the reports tool for the Guard Agent
    set_reports_tool(reports_tool)
    print("[Startup] Reports Tool initialized and connected to Guard Agent")
    print("[Startup] Application startup complete")

    yield

    print("[Shutdown] Application shutting down...")
    await mongodb.close()
    print("[Shutdown] Application shutdown complete")


logfire.configure()
logfire.instrument_pydantic_ai()

app = FastAPI(lifespan=lifespan)

# Include the router in the main application
app.include_router(
    chatbotRouter.router
)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "GuardOwl API - Security Report Assistant with Conversation History"}