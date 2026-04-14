from logging import getLogger
from asyncio import sleep

from faststream import Context
from faststream.rabbit import RabbitQueue, RabbitMessage
from aiogram import Bot
from aiogram.exceptions import (
    TelegramRetryAfter,
    TelegramForbiddenError,
    TelegramBadRequest,
    TelegramAPIError,
)

from ..client import broker
from ..dto import MailingTaskDto
from .producer import direct_exchange


logger = getLogger(name=__name__)
mailing_queue = RabbitQueue(name="send-mailing", routing_key="tg_id", durable=True)


@broker.subscriber(queue=mailing_queue, exchange=direct_exchange)
async def handle_mailing_message(
    task: MailingTaskDto,
    message: RabbitMessage,
    bot: Bot = Context("bot"),
) -> None:
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
        await message.ack()
    except TelegramRetryAfter as e:
        if task.retry_count > task.MAX_RETRIES:
            await message.nack(requeue=True)
            logger.error("Превышен лимит попыток для пользователя %s", task.tg_id)
            return
        task.retry_count += 1
        logger.warning(
            "Flood control для пользователя %s, повтор через %s сек.",
            task.tg_id,
            e.retry_after,
        )
        await sleep(e.retry_after)
        await message.nack(requeue=True)
    except TelegramForbiddenError:
        await message.ack()
        logger.info("Пользователь %s заблокировал бота, деактивируем.", task.tg_id)
    except TelegramBadRequest as e:
        await message.reject(requeue=False)
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
