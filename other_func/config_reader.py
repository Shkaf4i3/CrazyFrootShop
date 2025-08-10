from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    bot_key: SecretStr
    admin_id: str
    channel_id: str
    dsn: str
    pay_key: str
    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
    )


config = Settings()
