from logging import getLogger
from asyncio import get_event_loop

from celery import Celery
from aiogram.types import Message
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramAPIError,
    TelegramForbiddenError,
    TelegramRetryAfter,
)

from ..settings import settings, db_manage
from ..service import UserService
from ..repo import UnitOfWork, UserRepo


celery = Celery(
    main="Crazy Froot Shop",
    broker=settings.celery_broker,
    backend=settings.celery_backend,
)
logger = getLogger(__name__)


@celery.task
def mailing_message_to_users(
    message_type: str,
    message_text: str | None = None,
    message_media: str| None = None,
):
    async def start_mailing_message() -> None:
        async with Bot(
            token=settings.bot_token.get_secret_value(),
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        ) as bot:
            async with db_manage.session_factory() as session:
                unit_of_work = UnitOfWork(session=session)
                user_repo = UserRepo(session=session)
                user_service = UserService(unit_of_work=unit_of_work, user_repo=user_repo)
                available_users = await user_service.get_list_users()

                for user in available_users:
                    try:
                        if user.tg_id in settings.admin_id:
                            continue
                        if message_type == "photo":
                            await bot.send_photo(
                                chat_id=user.tg_id,
                                photo=message_media,
                                caption=message_text,
                            )
                        elif message_type == "document":
                            await bot.send_document(
                                chat_id=user.tg_id,
                                document=message_media,
                                caption=message_text,
                            )
                        elif message_type == "text":
                            await bot.send_message(
                                chat_id=user.tg_id,
                                text=message_text,
                            )
                    except (TelegramBadRequest, TelegramAPIError, TelegramForbiddenError, TelegramRetryAfter) as e:
                        logger.error(
                            "Ошибка отправки сообщения пользователю %s - %s",
                            user.tg_id,
                            str(e),
                        )

    loop = get_event_loop()
    loop.run_until_complete(future=start_mailing_message())
