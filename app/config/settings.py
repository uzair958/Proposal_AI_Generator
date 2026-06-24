from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    GROQ_API_KEY: str = ""
    SLACK_BOT_TOKEN: str = ""
    SLACK_SIGNING_SECRET: str = ""

    QDRANT_URL: str = ""
    QDRANT_API_KEY: str = ""

    DATABASE_URL: str = "sqlite:///./test.db"

    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


# 👇 IMPORTANT: DO NOT wrap in function
settings = Settings()