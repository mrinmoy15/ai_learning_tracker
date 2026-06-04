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

class ProgressItem(BaseModel):
    module_id: str
    course: str
    completed: bool


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
    total_c1: int
    total_c2: int
    done_c1: int
    done_c2: int
