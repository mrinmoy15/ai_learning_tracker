"""
Google OAuth flow:
1. GET /auth/login       → redirect to Google consent screen
2. GET /auth/callback    → exchange code for tokens, upsert user, return JWT
3. GET /auth/me          → return current user info from JWT
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
import httpx

from app.core.config import settings
from app.core.security import create_access_token, get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.schemas import TokenResponse, UserOut
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

router = APIRouter()

GOOGLE_AUTH_URL   = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL  = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO   = "https://www.googleapis.com/oauth2/v3/userinfo"


@router.get("/login")
async def login():
    """Redirect user to Google OAuth consent screen."""
    params = {
        "client_id":     settings.google_client_id,
        "redirect_uri":  settings.oauth_redirect_uri,
        "response_type": "code",
        "scope":         "openid email profile",
        "access_type":   "online",
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return RedirectResponse(f"{GOOGLE_AUTH_URL}?{query}")


@router.get("/callback")
async def callback(code: str, db: AsyncSession = Depends(get_db)):
    """Exchange Google auth code for tokens, upsert user, return JWT."""

    # 1. Exchange code for Google tokens
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(GOOGLE_TOKEN_URL, data={
            "code":          code,
            "client_id":     settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "redirect_uri":  settings.oauth_redirect_uri,
            "grant_type":    "authorization_code",
        })
        if token_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Google token exchange failed")

        google_tokens = token_resp.json()

        # 2. Get user info from Google
        userinfo_resp = await client.get(
            GOOGLE_USERINFO,
            headers={"Authorization": f"Bearer {google_tokens['access_token']}"},
        )
        if userinfo_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get Google user info")

        info = userinfo_resp.json()

    # 3. Upsert user in DB
    result = await db.execute(select(User).where(User.id == info["sub"]))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            id      = info["sub"],
            email   = info["email"],
            name    = info.get("name", ""),
            picture = info.get("picture"),
        )
        db.add(user)
    else:
        user.name    = info.get("name", user.name)
        user.picture = info.get("picture", user.picture)

    await db.commit()
    await db.refresh(user)

    # 4. Issue JWT and redirect to frontend
    token = create_access_token(user.id, user.email)
    return RedirectResponse(f"{settings.frontend_url}?token={token}")


@router.get("/me", response_model=UserOut)
async def me(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == current_user["sub"]))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserOut(id=user.id, email=user.email, name=user.name, picture=user.picture)
