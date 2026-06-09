"""
Progress endpoints:
GET  /progress       → return all progress for current user
POST /progress       → upsert a single module's completion state
POST /progress/bulk  → upsert multiple modules at once
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from app.core.security import get_current_user
from app.core.database import get_db
from app.models.progress import Progress
from app.schemas.schemas import AllProgressOut, ProgressOut, ProgressUpsert

router = APIRouter()

COURSE_TOTALS = {"c1": 8, "c2": 6, "c3": 8, "cap": 4}


@router.get("", response_model=AllProgressOut)
async def get_progress(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Progress).where(Progress.user_id == current_user["sub"])
    )
    rows = result.scalars().all()
    done = {course: 0 for course in COURSE_TOTALS}
    for r in rows:
        if r.completed and r.course in done:
            done[r.course] += 1
    return AllProgressOut(
        progress=  [ProgressOut.model_validate(r) for r in rows],
        totals=    COURSE_TOTALS,
        done=      done,
    )


@router.post("", response_model=ProgressOut)
async def upsert_progress(
    body: ProgressUpsert,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Progress).where(
            Progress.user_id   == current_user["sub"],
            Progress.module_id == body.module_id,
        )
    )
    row = result.scalar_one_or_none()
    now = datetime.now(timezone.utc)

    if row is None:
        row = Progress(
            user_id=      current_user["sub"],
            course=       body.course,
            module_id=    body.module_id,
            completed=    body.completed,
            completed_at= now if body.completed else None,
            updated_at=   now,
        )
        db.add(row)
    else:
        row.completed    = body.completed
        row.completed_at = now if body.completed else None
        row.updated_at   = now

    await db.commit()
    await db.refresh(row)
    return ProgressOut.model_validate(row)


@router.post("/bulk", response_model=AllProgressOut)
async def bulk_upsert(
    items: list[ProgressUpsert],
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    for body in items:
        result = await db.execute(
            select(Progress).where(
                Progress.user_id   == current_user["sub"],
                Progress.module_id == body.module_id,
            )
        )
        row = result.scalar_one_or_none()
        if row is None:
            db.add(Progress(
                user_id=      current_user["sub"],
                course=       body.course,
                module_id=    body.module_id,
                completed=    body.completed,
                completed_at= now if body.completed else None,
                updated_at=   now,
            ))
        else:
            row.completed    = body.completed
            row.completed_at = now if body.completed else None
            row.updated_at   = now

    await db.commit()

    result = await db.execute(
        select(Progress).where(Progress.user_id == current_user["sub"])
    )
    rows = result.scalars().all()
    done = {course: 0 for course in COURSE_TOTALS}
    for r in rows:
        if r.completed and r.course in done:
            done[r.course] += 1
    return AllProgressOut(
        progress= [ProgressOut.model_validate(r) for r in rows],
        totals=   COURSE_TOTALS,
        done=     done,
    )
