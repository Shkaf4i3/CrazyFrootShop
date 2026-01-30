from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from .config import settings


class DataBaseManager:
    def __init__(self):
        self.session_engine = create_async_engine(
            url=settings.dsn.encoded_string(),
        )
        self.session_factory = async_sessionmaker(
            bind=self.session_engine,
        )


db_manage = DataBaseManager()
