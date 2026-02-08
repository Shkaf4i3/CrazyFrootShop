from datetime import datetime, timezone

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, BigInteger, Integer, UUID, func

from .base import Base


class User(Base):
    __tablename__ = "User"

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, server_default=func.uuidv7())
    tg_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    tg_username: Mapped[str] = mapped_column(String, nullable=False)
    balance: Mapped[int] = mapped_column(Integer, default=0, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(tz=timezone.utc),
        nullable=False,
    )
