from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # App
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Database
    DATABASE_URL: str = "postgresql://scraper:scraper123@db:5432/scraper_db"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # Apify (paid option)
    APIFY_API_TOKEN: Optional[str] = None

    # Twitter API (paid option)
    TWITTER_BEARER_TOKEN: Optional[str] = None
    TWITTER_API_KEY: Optional[str] = None
    TWITTER_API_SECRET: Optional[str] = None

    # Reddit API (free)
    REDDIT_CLIENT_ID: Optional[str] = None
    REDDIT_CLIENT_SECRET: Optional[str] = None
    REDDIT_USER_AGENT: str = "SocialScraper/1.0"

    # Instagram (free/instaloader)
    INSTAGRAM_USERNAME: Optional[str] = None
    INSTAGRAM_PASSWORD: Optional[str] = None

    # Scraper timeout guard (seconds) for long-running third-party calls.
    SCRAPER_TIMEOUT_SECONDS: int = 90
    # Comma-separated origins for CORS (set "*" only for local/testing).
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
