# Guard Owl API

A FastAPI-based backend for the Guard Owl security chatbot. Uses Pydantic AI agents powered by Google Gemini to answer security guard queries and retrieve security reports from a ChromaDB vector database.

## Features

- **AI-Powered Chat Agent**: Conversational agent that answers security-related queries
- **Semantic Search**: Natural language search over security reports using ChromaDB
- **Metadata Filtering**: Query reports by site ID, guard ID, date, and other attributes
- **Report Parsing**: Converts natural language queries into structured database queries
- **Auto-Initialization**: ChromaDB automatically ingests sample data on first run
- **Observability**: Logfire instrumentation for monitoring and debugging
- **Fast Development**: Built with FastAPI and uv for rapid iteration

## Project Structure

```
api/
├── src/
│   ├── agents/
│   │   ├── guardAgent.py          # Main conversational AI agent
│   │   └── parsingAgent.py        # Parses queries into structured params
│   ├── tools/
│   │   ├── reportsToolClass.py    # Reports tool wrapper for agent
│   │   └── retrieveReports.py     # ChromaDB query execution
│   ├── collections/
│   │   ├── chromadb.py            # Database initialization and ingestion
│   │   └── data.json              # Sample security reports
│   ├── models/
│   │   └── chromadb.py            # ChromaQueryParams schema
│   ├── routers/
│   │   └── chatbotRouter.py       # /chat endpoint definition
│   ├── ai/
│   │   └── allModels.py           # Gemini model configuration
│   └── utils/
│       └── constants.py           # Environment variables and config
├── main.py                        # FastAPI application entry point
├── pyproject.toml                 # Project dependencies
└── uv.lock                        # Locked dependencies
```

## Installation

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager
- Google Gemini API key
- ChromaDB API key and tenant (free at [trychroma.com](https://www.trychroma.com/))

### Setup

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Create a `.env` file** with your API credentials:
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env`** and add your API keys:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   CHROMA_API_KEY=your_chroma_api_key_here
   CHROMA_TENANT=your_chroma_tenant_id_here
   CHROMA_DATABASE=reports_dev
   ```

## Development

Start the development server with auto-reload:

```bash
uv run fastapi dev
```

The API will be available at `http://127.0.0.1:8000`

### First Run

On first startup, the API will:
1. Initialize the ChromaDB collection
2. Automatically ingest sample reports from `src/collections/data.json`
3. Make the database ready for queries

You'll see startup logs like:
```
[Startup] Initializing ChromaDB...
[Startup] ChromaDB collection has 0 documents
[Startup] Collection is empty. Ingesting data from src/collections/data.json...
[Startup] Data ingestion complete. Collection now has X documents
```

## Production

Run the production server:

```bash
uv run fastapi run
```

## API Endpoints

### Root Endpoint

```bash
GET /
```

Returns a welcome message.

### Chat Endpoint

```bash
POST /chat
Content-Type: application/json

{
  "query": "Show me all reports from site S04"
}
```

**Response (Success):**
```json
{
  "query": "Show me all reports from site S04",
  "response": {
    "output": "## Reports from Site S04\n\n1. **Report R001**..."
  }
}
```

**Response (Error):**
```json
{
  "detail": "Error message"
}
```

## Agent System

### Guard Agent

The main conversational agent (`src/agents/guardAgent.py`) handles:
- Security report queries
- Shift schedules
- Support contact information
- General security questions

**Available Tools:**
- `retrieve_security_reports()` - Searches ChromaDB for relevant reports
- `provide_shift_schedule()` - Returns shift schedules
- `call_support()` - Provides support contact info

### Query Types

The system supports two types of ChromaDB queries:

1. **Semantic Search**: Natural language queries like "white vehicle incidents" or "loitering near gates"
   - Uses vector similarity search
   - Returns relevance scores

2. **Metadata Filtering**: Structured queries like "all reports from Site S04 on August 30th"
   - Direct metadata filtering
   - Exact matches on `siteId`, `guardId`, `date`

### Response Formatting

Agent responses use Markdown formatting:
- **Bold** for site IDs, guard IDs, key findings
- `##` headings for sections
- Bullet points for lists
- Code formatting for IDs

## ChromaDB Configuration

ChromaDB persists data to `./chroma_db` by default.

**Report Metadata Structure:**
```json
{
  "id": "R001",
  "text": "Report content for semantic search...",
  "metadata": {
    "siteId": "S04",
    "guardId": "G03",
    "date": "2024-08-30"
  }
}
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | Google Gemini API key |
| `CHROMA_API_KEY` | ChromaDB API key |
| `CHROMA_TENANT` | ChromaDB tenant ID |
| `CHROMA_DATABASE` | ChromaDB database name |

## Package Management

```bash
# Add a new dependency
uv add package-name

# Update dependencies
uv lock --upgrade

# Install dependencies
uv sync
```

## Features Implemented

✅ AI-powered conversational agent with Pydantic AI
✅ Semantic search over security reports
✅ Metadata filtering (site, guard, date)
✅ Natural language query parsing
✅ Auto-ingestion of sample data
✅ Markdown-formatted responses
✅ Report relevance scoring
✅ Error handling and validation
✅ Logfire observability
✅ CORS middleware for frontend integration
✅ Tool-based agent architecture

## Technology Stack

- **Framework**: FastAPI
- **AI/LLM**: Pydantic AI with Google Gemini (gemini-2.0-flash)
- **Vector Database**: ChromaDB (cloud-hosted)
- **Observability**: Logfire
- **Package Manager**: uv
- **Python**: 3.13+

## Notes

- The parsing agent currently uses regex heuristics but is designed to be replaced with an LLM-based parser
- ChromaDB collection is automatically created on first run
- Logfire instrumentation requires separate Logfire account setup
- The Guard Agent uses strict relevance filtering to avoid mentioning irrelevant reports
- All responses are formatted in Markdown for the frontend chat interface

## Troubleshooting

**ChromaDB connection errors:**
- Verify your `CHROMA_API_KEY` and `CHROMA_TENANT` in `.env`
- Check your internet connection (ChromaDB is cloud-hosted)

**Gemini API errors:**
- Verify your `GEMINI_API_KEY` in `.env`
- Check your API quota at [Google AI Studio](https://aistudio.google.com/)

**Empty responses:**
- Check that data was ingested on startup
- Verify ChromaDB collection has documents

## Frontend Integration

This API is designed to work with the Guard Owl chat interface (see `../chatbot/README.md`). The frontend expects:
- POST requests to `/chat` endpoint
- JSON request body with `query` field
- JSON response with `response.output` field containing Markdown
