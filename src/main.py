from contextlib import asynccontextmanager
from typing import Any, Annotated
from logging import basicConfig, INFO

from fastapi import FastAPI, Depends
from uvicorn import run
from aiogram.types import Update, BotCommandScopeAllPrivateChats

from .app import create_dispatcher, create_bot
from .settings import settings, db_manage
from .aiogram_functions import available_commands
from .model import Base
from .deps import services
from .service import UserService, AccountService


bot = create_bot()
dp = create_dispatcher()


@asynccontextmanager
async def lifespan(_: FastAPI):
    basicConfig(
        level=INFO,
        datefmt=r"%Y-%m-%d %H:%M:%S",
        format=r"[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s",
    )

    await bot.set_webhook(url=settings.webhook_url, drop_pending_updates=True)
    exists_commands = await bot.get_my_commands(scope=BotCommandScopeAllPrivateChats())
    if not exists_commands:
        await bot.set_my_commands(
            commands=available_commands,
            scope=BotCommandScopeAllPrivateChats(),
        )

    async with db_manage.session_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await bot.session.close()


app = FastAPI(lifespan=lifespan, docs_url="/", redoc_url=None)


@app.post("/webhook")
async def handle_webhook_update(
    update: dict[str, Any],
    user_service: Annotated[UserService, Depends(services.get_user_service)],
    account_service: Annotated[AccountService, Depends(services.get_account_service)],
) -> None:
    new_update = Update.model_validate(update, by_alias=True, by_name=True)
    dp["user_service"] = user_service
    dp["account_service"] = account_service
    await dp.feed_update(bot=bot, update=new_update)


if __name__ == "__main__":
    run(app="main:app", reload=True)
