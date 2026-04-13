from pydantic import BaseModel


class MailingTaskDto(BaseModel):
    tg_id: int
    message_type: str
    retry_count: int = 0
    MAX_RETRIES: int = 3
    message_text: str | None = None
    message_media: str | None = None
