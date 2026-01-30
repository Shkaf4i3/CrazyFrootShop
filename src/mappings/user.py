from ..model import User
from ..dto import UserDto


def mapping_user(user: User) -> UserDto:
    return UserDto(
        tg_id=user.tg_id,
        tg_username=user.tg_username,
        balance=user.balance,
        created_at=user.created_at,
    )
