from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str | None = None
    parser_backend: str = "fake"
    min_parse_confidence: float = 0.6

    model_config = ConfigDict(env_file=".env")


settings = Settings()
