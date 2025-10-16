from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

from src.utils.constants import GEMINI, GEMINI_API_KEY

google_provider = GoogleProvider(api_key=GEMINI_API_KEY)
gemini_model = GoogleModel(GEMINI, provider=google_provider)