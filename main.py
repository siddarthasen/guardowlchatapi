# main.py

from fastapi import FastAPI
from src.routers import chatbotRouter
import logfire

logfire.configure()
logfire.instrument_pydantic_ai()

app = FastAPI()

# Include the router in the main application
# All endpoints in items.py will be prefixed with '/items'
app.include_router(
    chatbotRouter.router
)

# You can keep your root path here if you want:
@app.get("/")
async def root():
    return {"message": "Hello World"}