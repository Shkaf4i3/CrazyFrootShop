from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AccountDto(BaseModel):
    id: UUID
    type_platform: str
    login: str
    password: str
    created_at: datetime
