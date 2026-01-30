from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..model import User


class UserRepo:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def save_user(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user


    async def get_user_by_tg_id(self, tg_id: int) -> User | None:
        stmt = select(User).where(User.tg_id == tg_id)
        result = await self.session.execute(statement=stmt)
        return result.scalar()


    async def get_list_users(self) -> list[User]:
        stmt = select(User)
        result = await self.session.execute(statement=stmt)
        return result.scalars().all()
