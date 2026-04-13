from pydantic import BaseModel


class MailingTaskDto(BaseModel):
    tg_id: int
    message_type: str
    message_text: str | None = None
    message_media: str | None = None
