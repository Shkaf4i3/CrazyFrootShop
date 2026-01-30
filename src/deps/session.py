from ..settings import db_manage


async def open_session():
    async with db_manage.session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
