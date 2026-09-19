import os
from typing import Optional
from dotenv import load_dotenv, dotenv_values
from pydantic_settings import BaseSettings, SettingsConfigDict

# Explicitly load .env with override=True so placeholder OS environment variables don't shadow .env
load_dotenv(override=True)

class Settings(BaseSettings):
    # LLM Settings
    LLM_MODEL: str = "deepseek-v4.1"
    LLM_BASE_URL: str = "https://vyceai.com/v1"
    LLM_API_KEY: str = ""
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 4096

    # Supabase Settings
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None
    REQUIRE_AUTH: bool = True

    # MCP Settings
    MCP_CONFIG_PATH: str = "mcp_servers.json"

    # Server Settings
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Fallback: if OS environment variable injected 'none' or placeholder, grab real value from .env file
dotenv_vals = dotenv_values(".env")
if settings.LLM_API_KEY.lower() in ("none", "null", "undefined", "") and dotenv_vals.get("LLM_API_KEY"):
    settings.LLM_API_KEY = dotenv_vals["LLM_API_KEY"]
if dotenv_vals.get("LLM_MODEL") and settings.LLM_MODEL != dotenv_vals["LLM_MODEL"]:
    settings.LLM_MODEL = dotenv_vals["LLM_MODEL"]
if dotenv_vals.get("LLM_BASE_URL") and settings.LLM_BASE_URL != dotenv_vals["LLM_BASE_URL"]:
    settings.LLM_BASE_URL = dotenv_vals["LLM_BASE_URL"]

