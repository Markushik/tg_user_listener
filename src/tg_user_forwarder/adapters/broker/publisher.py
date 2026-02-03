from __future__ import annotations

import orjson
from aio_pika import Message
from aiogram.types import Update
from faststream.rabbit import ExchangeType, RabbitBroker, RabbitExchange
from opentelemetry.propagate import inject

from tg_user_forwarder.settings.models import RabbitSettings


class UpdatesPublisher:
    def __init__(self, broker: RabbitBroker, settings: RabbitSettings) -> None:
        exchange = RabbitExchange(
            name=settings.exchange,
            type=ExchangeType.DIRECT,
            durable=True,
        )
        publishers_by_routing_key = {
            settings.funnel_routing_key: broker.publisher(exchange=exchange, routing_key=settings.funnel_routing_key),
            settings.router_routing_key: broker.publisher(exchange=exchange, routing_key=settings.router_routing_key),
            settings.other_routing_key: broker.publisher(exchange=exchange, routing_key=settings.other_routing_key),
        }

        self.publishers_by_routing_key = publishers_by_routing_key
        self.default_routing_key = settings.other_routing_key

    async def publish(self, routing_key: str, update: Update) -> None:
        publisher = self.publishers_by_routing_key.get(routing_key)
        if publisher is None:
            publisher = self.publishers_by_routing_key[self.default_routing_key]

        headers: dict[str, str] = {}
        inject(headers)

        payload = orjson.dumps(update.model_dump(mode="json"))
        message = Message(
            payload,
            content_type="application/json",
            headers=headers,
        )

        await publisher.publish(message)

