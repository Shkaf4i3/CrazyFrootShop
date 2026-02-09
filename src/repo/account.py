from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..model import Account


class AccountRepo:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def save_account(self, account: Account) -> Account:
        self.session.add(account)
        await self.session.flush()
        await self.session.refresh(account)
        return account


    async def get_available_account(self) -> Account | None:
        stmt = select(Account).order_by(Account.created_at.desc()).limit(1)
        result = await self.session.execute(statement=stmt)
        return result.scalar()


    async def get_count_accounts(self, type_platform: str) -> int | None:
        stmt = (
            select(func.count())
            .select_from(Account)
            .where(Account.type_platform == type_platform)
        )
        result = await self.session.execute(statement=stmt)
        return result.scalar()


    async def get_account_by_login_and_platform_type(self, login: str, type_platform: str) -> Account | None:
        stmt = select(Account).where(
            Account.login == login,
            Account.type_platform == type_platform,
        )
        result = await self.session.execute(statement=stmt)
        return result.scalar()

    async def get_account_by_id(self, id: str) -> Account | None:
        stmt = select(Account).where(Account.id == id)
        result = await self.session.execute(statement=stmt)
        return result.scalar()


    async def get_account_by_type_platform(self, type_platform: str) -> Account | None:
        stmt = (
            select(Account)
            .where(Account.type_platform == type_platform)
            .limit(1)
            .order_by(Account.created_at.desc())
        )
        result = await self.session.execute(statement=stmt)
        return result.scalar()


    async def delete_account(self, account: Account) -> None:
        await self.session.flush()
        await self.session.delete(account)
        self.session.expire_all()
