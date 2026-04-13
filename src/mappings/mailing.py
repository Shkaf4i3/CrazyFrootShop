from ..dto import MailingTaskDto, UserDto


def mapping_mailing(
    user: UserDto,
    message_type: str,
    message_text: str | None = None,
    message_media: str | None = None,
) -> MailingTaskDto:
    return MailingTaskDto(
        tg_id=user.tg_id,
        message_type=message_type,
        message_text=message_text,
        message_media=message_media,
    )
