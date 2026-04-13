from logging import getLogger
from asyncio import sleep

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
from ..dto import MailingTaskDto
from ..mappings import mailing_mappings
from ..client import broker


logger = getLogger(__name__)
bot = Bot(
    token=settings.bot_token.get_secret_value(),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)


async def mailing_message_to_users(
    message_type: str,
    message_text: str | None = None,
    message_media: str| None = None,
) -> None:
    async with db_manage.session_factory() as session:
        unit_of_work = UnitOfWork(session=session)
        user_repo = UserRepo(session=session)
        user_service = UserService(unit_of_work=unit_of_work, user_repo=user_repo)
        available_users = await user_service.get_list_users()
        for user in available_users:
            if user.tg_id in settings.admin_ids:
                continue
            task = mailing_mappings.mapping_mailing(
                user=user,
                message_type=message_type,
                message_text=message_text,
                message_media=message_media,
            )
            await broker.publish(message=task, queue="send-mailing")


@broker.subscriber(queue="send-mailing")
async def handle_mailing_message(task: MailingTaskDto) -> None:
    try:
        if task.message_type == "photo":
            await bot.send_photo(
                chat_id=task.tg_id,
                photo=task.message_media,
                caption=task.message_text,
            )
        elif task.message_type == "document":
            await bot.send_document(
                chat_id=task.tg_id,
                document=task.message_media,
                caption=task.message_text,
            )
        elif task.message_type == "text":
            await bot.send_message(
                chat_id=task.tg_id,
                text=task.message_text,
            )
    except TelegramRetryAfter as e:
        logger.warning(
            "Flood control для пользователя %s, повтор через %s сек.",
            task.tg_id,
            e.retry_after,
        )
        await sleep(e.retry_after)
        await broker.publish(task, queue="send-mailing")
    except TelegramForbiddenError:
        logger.info("Пользователь %s заблокировал бота, деактивируем.", task.tg_id)
    except TelegramBadRequest as e:
        logger.error(
            "Невалидный запрос для пользователя %s: %s",
            task.tg_id,
            str(e),
        )
    except TelegramAPIError as e:
        logger.exception(
            "Ошибка Telegram API при отправке пользователю %s: %s",
            task.tg_id,
            str(e),
        )
    except Exception as e:
        logger.error("Произошла неожиданная ошибка - %s", str(e))
