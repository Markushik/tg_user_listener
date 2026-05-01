from typing import Mapping
from urllib.parse import urljoin

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    token: str = Field(alias="BOT_TOKEN_A")
    bot_key: str = Field(alias="BOT_KEY_A")

    webhook_base_url: str = Field(alias="BOT_WEBHOOK_BASE_URL")
    webhook_path: str = Field(alias="BOT_WEBHOOK_PATH")
    webhook_secret: str = Field(alias="BOT_WEBHOOK_SECRET")
    webhook_enabled: bool = Field(default=True, alias="BOT_WEBHOOK_ENABLED")

    @property
    def webhook_url(self) -> str:
        return urljoin(
            self.webhook_base_url.rstrip("/") + "/",
            self.webhook_path.lstrip("/"),
        )


class RabbitSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RABBITMQ_", extra="ignore")

    host: str
    port: int
    user: str
    password: str
    vhost: str

    audience: str = "user"

    exchange: str = "tg_updates.inbound"
    queues: Mapping[str, str] = Field(
        default_factory=lambda: {
            "tg_updates.user.private": "updates.user.private",
            "tg_updates.user.group": "updates.user.group",
            "tg_updates.user.other": "updates.user.other",
        }
    )

    retry_exchange: str = "tg_updates.retry"
    retry_queue_suffix: str = ".retry"
    retry_routing_key_suffix: str = ".retry"
    retry_ttl_ms: int = 30_000

    @property
    def url(self) -> str:
        return f"amqp://{self.user}:{self.password}@{self.host}:{self.port}{self.vhost}"


class Settings(BaseSettings):
    bot: BotSettings = Field(default_factory=BotSettings)
    rabbit: RabbitSettings = Field(default_factory=RabbitSettings)
