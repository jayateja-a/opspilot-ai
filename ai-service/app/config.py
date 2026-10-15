from pathlib import Path
from typing import Literal
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_dsn: str = "postgresql://opspilot:opspilot-local-only@localhost:5432/opspilot"
    agent_token: str = "local-agent-token"
    ai_mode: Literal["demo", "openai"] = "demo"
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    embedding_model: str = "text-embedding-3-small"
    fixtures_dir: Path = Path(__file__).resolve().parents[2] / "fixtures"

settings = Settings()
