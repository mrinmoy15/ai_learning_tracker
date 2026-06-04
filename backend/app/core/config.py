from pydantic_settings import BaseSettings
from typing import list


class Settings(BaseSettings):
    # ── Database ──────────────────────────────────────────────────────────────
    database_url: str                          # Neon PostgreSQL connection string

    # ── Google OAuth ──────────────────────────────────────────────────────────
    google_client_id: str
    google_client_secret: str
    oauth_redirect_uri: str = "https://your-cloudrun-url/auth/callback"

    # ── JWT ───────────────────────────────────────────────────────────────────
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7     # 7 days

    # ── CORS ──────────────────────────────────────────────────────────────────
    allowed_origins: list[str] = [
        "https://yourusername.github.io",
        "http://localhost:5500",               # Live Server local dev
        "http://127.0.0.1:5500",
    ]

    class Config:
        env_file = ".env"


settings = Settings()
