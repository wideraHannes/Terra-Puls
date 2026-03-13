from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/terrapulse"
    REDIS_URL: str = "redis://redis:6379/0"
    WORLDNEWS_API_KEY: str = ""
    CELERY_BROKER_URL: str = "redis://redis:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/2"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:3001", "http://frontend:3000"]


settings = Settings()
