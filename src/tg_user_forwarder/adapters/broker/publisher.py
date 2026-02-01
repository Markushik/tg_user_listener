from __future__ import annotations

import orjson

from aio_pika import Message
from aiogram.types import Update
from faststream.rabbit import RabbitBroker

from tg_user_forwarder.application.constants import group_route, other_route, personal_route
from tg_user_forwarder.settings.models import RabbitSettings


class UpdatesPublisher:
    def __init__(self, broker: RabbitBroker, settings: RabbitSettings) -> None:
        self.personal_publisher = broker.publisher(queue=settings.personal_queue, routing_key=settings.personal_queue)
        self.group_publisher = broker.publisher(queue=settings.group_queue, routing_key=settings.group_queue)
        self.other_publisher = broker.publisher(queue=settings.other_queue, routing_key=settings.other_queue)

    async def publish(self, routing_key: str, update: Update) -> None:
        if routing_key == personal_route:
            publisher = self.personal_publisher
        elif routing_key == group_route:
            publisher = self.group_publisher
        else:
            publisher = self.other_publisher

        body = orjson.dumps(update.model_dump(mode="json"))
        await publisher.publish(Message(body, content_type="application/json"))
