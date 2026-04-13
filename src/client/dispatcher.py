from aiogram import Dispatcher

from ..handlers import user_router, admin_router
from ..aiogram_functions import CallbackAnswer


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.include_routers(
        user_router,
        admin_router,
    )
    dp.callback_query.middleware(CallbackAnswer())
    return dp
