from faststream.rabbit import RabbitExchange, ExchangeType

from ..settings import db_manage, settings
from ..repo import UnitOfWork, UserRepo
from ..service import UserService
from ..mappings import mailing_mappings
from ..client import broker


direct_exchange = RabbitExchange(
    name="notifications",
    type=ExchangeType.DIRECT,
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
            await broker.publish(message=task, exchange=direct_exchange, routing_key="tg_id")
