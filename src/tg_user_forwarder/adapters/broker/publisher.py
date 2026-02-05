from __future__ import annotations

import orjson
from aio_pika import Message
from aiogram.enums import ChatType
from aiogram.types import Update
from faststream.rabbit import ExchangeType, RabbitBroker, RabbitExchange
from opentelemetry.propagate import inject

from tg_user_forwarder.settings.models import RabbitSettings


class UpdatesPublisher:
    def __init__(self, broker: RabbitBroker, settings: RabbitSettings) -> None:
        self.exchange = RabbitExchange(
            name=settings.exchange,
            type=ExchangeType.TOPIC,
            durable=True,
        )
        self.audience = settings.audience

        self.publishers = {
            "private": broker.publisher(exchange=self.exchange, routing_key=f"updates.{self.audience}.private"),
            "group": broker.publisher(exchange=self.exchange, routing_key=f"updates.{self.audience}.group"),
            "other": broker.publisher(exchange=self.exchange, routing_key=f"updates.{self.audience}.other"),
        }

    async def publish(self, update: Update, chat_type: ChatType | None) -> None:
        headers: dict[str, str] = {}
        inject(headers)

        payload = orjson.dumps(update.model_dump(mode="json"))
        message = Message(payload, content_type="application/json", headers=headers)

        if chat_type == ChatType.PRIVATE:
            scope = "private"
        elif chat_type in (ChatType.GROUP, ChatType.SUPERGROUP):
            scope = "group"
        else:
            scope = "other"

        await self.publishers[scope].publish(message)
