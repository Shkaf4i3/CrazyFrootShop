from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, TypeDecorator, DateTime
from cryptography.fernet import Fernet

from ..model import Base
from ..settings import settings


# Create new fernet key and save him in .env file
fernet = Fernet(key=settings.fernet_key)


class EncryptedString(TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        return fernet.encrypt(value.encode()).decode()

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return fernet.decrypt(value.encode()).decode()


class Account(Base):
    __tablename__ = "Account"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, unique=True, default=lambda: str(uuid4()),
    )
    type_platform: Mapped[str] = mapped_column(String, nullable=False)
    login: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(EncryptedString(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(tz=timezone.utc),
        nullable=False,
    )
