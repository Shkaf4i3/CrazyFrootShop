from datetime import datetime

from pydantic import BaseModel


class AccountDto(BaseModel):
    id: str
    type_platform: str
    login: str
    password: str
    created_at: datetime
