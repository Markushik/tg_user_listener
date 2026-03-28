import os
from typing import Mapping

from pydantic import BaseModel, Field


class BotSettings(BaseModel):
    token: str = "6996207760:AAEQbsRpJCuWp7bKAfk24t7RecPqskBLpZQ"

    webhook_base_url: str = Field(default_factory=lambda: os.getenv("WEBHOOK_BASE_URL", "https://example.com"))
    webhook_path: str = Field(default_factory=lambda: os.getenv("WEBHOOK_PATH", "/telegram/webhook"))
    webhook_secret: str = Field(default_factory=lambda: os.getenv("WEBHOOK_SECRET", "my-secret"))


class RabbitSettings(BaseModel):
    url: str = Field(default="amqp://guest:guest@localhost:5672")
    audience: str = "user"

    # main inbound topology
    exchange: str = Field(default="tg_updates.inbound")
    queues: Mapping[str, str] = Field(
        default_factory=lambda: {
            "tg_updates.user.private": "updates.user.private",
            "tg_updates.user.group": "updates.user.group",
            "tg_updates.user.other": "updates.user.other",
        },
        description="Mapping of queue name to routing key",
    )

    # retry / poison topology
    retry_exchange: str = "tg_updates.retry"
    retry_queue_suffix: str = ".retry"
    retry_routing_key_suffix: str = ".retry"
    retry_ttl_ms: int = 30_000


class Settings(BaseModel):
    bot: BotSettings = Field(default_factory=BotSettings)
    rabbit: RabbitSettings = Field(default_factory=RabbitSettings)