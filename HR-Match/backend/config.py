from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    TAVILY_API_KEY: str = ""
    MAX_REFLECTIONS: int = 2

    model_config = {
        "env_file": Path(__file__).parent / "deepseek.env",
        "case_sensitive": False,
    }


settings = Settings()
