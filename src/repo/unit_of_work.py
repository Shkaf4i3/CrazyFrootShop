from contextlib import asynccontextmanager
from functools import wraps

from sqlalchemy.ext.asyncio import AsyncSession


class UnitOfWork:
    def __init__(self, session: AsyncSession):
        self.session = session


    @asynccontextmanager
    async def transaction(self):
        try:
            yield self.session
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise e


def transactional(method):
    @wraps(method)
    async def wrapper(self, *args, **kwargs):
        if not hasattr(self, "unit_of_work"):
            raise AttributeError("Unit of Work not initialized.")
        async with self.unit_of_work.transaction():
            return await method(self, *args, **kwargs)

    return wrapper
