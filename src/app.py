from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode

from .settings import settings
from .handlers import admin_router, user_router
from .aiogram_functions import CallbackAnswer


def create_bot() -> Bot:
    bot = Bot(
        token=settings.bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML,),
    )
    return bot


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.include_routers(
        user_router,
        admin_router,
    )
    dp.callback_query.middleware(CallbackAnswer())
    return dp
