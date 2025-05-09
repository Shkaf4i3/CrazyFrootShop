from asyncio import run
from logging import basicConfig, INFO

from aiogram import Dispatcher, Bot
from aiogram.types import BotCommandScopeAllPrivateChats
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode

from handlers.user_private import user_private_router
from handlers.admin_private import admin_private_router
from cmd_list import private
from handlers.database import create_table
from handlers.classes_functions import CheckSubscribe, AntiFloodMiddleware
from handlers.config_reader import config


async def main() -> None:
    await create_table()
    bot = Bot(config.bot_key.get_secret_value(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.message.middleware(AntiFloodMiddleware())
    dp.message.middleware(CheckSubscribe())

    dp.include_routers(user_private_router, admin_private_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=private, scope=BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot)


if __name__ == "__main__":
    basicConfig(
        level=INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
        format="[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s",
        )

    try:
        run(main(), loop_factory=None)
    except KeyboardInterrupt:
        print('Exit')
