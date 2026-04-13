from typing import Dict, List

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, PostgresDsn


class Settings(BaseSettings):
    bot_token: SecretStr
    webhook_url: str
    rabbitmq_url: str
    dsn: PostgresDsn
    admin_ids: List[int]
    admin_username: str
    user_agreement: str
    fernet_key: str
    available_platforms: Dict[str, str]
    crypto_bot_token: str
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
