from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str]           = mapped_column(String, primary_key=True)  # Google sub
    email: Mapped[str]        = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str]         = mapped_column(String, nullable=False)
    picture: Mapped[str]      = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
