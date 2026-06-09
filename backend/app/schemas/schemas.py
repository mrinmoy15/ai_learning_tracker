from pydantic import BaseModel, EmailStr
from datetime import datetime


# ── Auth ──────────────────────────────────────────────────────────────────────

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


class UserOut(BaseModel):
    id: str
    email: EmailStr
    name: str
    picture: str | None


# ── Progress ──────────────────────────────────────────────────────────────────

class ProgressUpsert(BaseModel):
    module_id: str
    course: str
    completed: bool


class ProgressOut(BaseModel):
    module_id: str
    course: str
    completed: bool
    completed_at: datetime | None
    updated_at: datetime

    class Config:
        from_attributes = True


class AllProgressOut(BaseModel):
    progress: list[ProgressOut]
    totals: dict[str, int]   # e.g. {"c1": 8, "c2": 6, "c3": 8, "cap": 4}
    done: dict[str, int]     # e.g. {"c1": 3, "c2": 0, "c3": 0, "cap": 0}
