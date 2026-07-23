# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
import os
# pyrefly: ignore [missing-import]
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

AI_PROVIDERS = os.getenv("AI_PROVIDERS", "gemini,grok").split(",")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")
GEMINI_MODELS = [
    os.getenv("GEMINI_MODEL_1"),
    os.getenv("GEMINI_MODEL_2")
]

GROK_API_KEY = os.getenv("GROK_API_KEY")
GROK_MODEL = os.getenv("GROK_MODEL")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")

HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL = os.getenv("HF_MODEL")

UNIPILE_BASE_URL=os.getenv("UNIPILE_BASE_URL")
UNIPILE_API_KEY=os.getenv("UNIPILE_API_KEY")
UNIPILE_ACCOUNT_ID=os.getenv("UNIPILE_ACCOUNT_ID")

MONGODB_URI = os.getenv("MONGODB_URI")

class Settings(BaseSettings):
    database_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
