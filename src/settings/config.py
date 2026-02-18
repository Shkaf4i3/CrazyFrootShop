from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, PostgresDsn


class Settings(BaseSettings):
    bot_token: SecretStr
    redis_url: str
    data_ttl: int
    state_ttl: int
    webhook_url: str
    dsn: PostgresDsn
    admin_id: list[int]
    admin_username: str
    user_agreement: str
    fernet_key: str
    available_platforms: dict[str, str]
    crypto_bot_token: str
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
