import asyncio
import logging
from os import getenv
from dotenv import load_dotenv

from aiogram import Dispatcher, Bot
from aiogram.types import BotCommandScopeAllPrivateChats
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode

from handlers.user_private import user_private_router
from handlers.admin_private import admin_private_router
from cmd_list import private
from handlers.database import create_table
from handlers.classes_functions import CheckSubscribe, AntiFloodMiddleware


async def main() -> None:
    load_dotenv()

    await create_table()
    bot = Bot(getenv('bot_key'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.message.middleware(AntiFloodMiddleware())
    dp.message.middleware(CheckSubscribe())

    dp.include_routers(user_private_router, admin_private_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=private, scope=BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot)


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main(), loop_factory=None)
    except KeyboardInterrupt:
        print('Exit')
