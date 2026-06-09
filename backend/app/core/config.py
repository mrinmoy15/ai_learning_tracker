from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── Database ──────────────────────────────────────────────────────────────
    database_url: str

    # ── Google OAuth ──────────────────────────────────────────────────────────
    google_client_id: str = Field(..., min_length=1)
    google_client_secret: str = Field(..., min_length=1)
    oauth_redirect_uri: str = "https://your-cloudrun-url/auth/callback"
    frontend_url: str = "http://localhost:3000"

    # ── JWT ───────────────────────────────────────────────────────────────────
    jwt_secret: str = Field(..., min_length=32)
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7      # 7 days

    # ── CORS ──────────────────────────────────────────────────────────────────
    allowed_origins: list[str] = [
        "https://mrinmoy15.github.io",
        "http://localhost:3000",
    ]

    class Config:
        env_file = ".env"


settings = Settings()
