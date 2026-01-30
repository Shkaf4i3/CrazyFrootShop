from datetime import datetime

from pydantic import BaseModel


class UserDto(BaseModel):
    tg_id: int
    tg_username: str
    balance: int
    created_at: datetime
