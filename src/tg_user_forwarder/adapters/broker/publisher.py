from __future__ import annotations

import orjson

from aio_pika import Message
from aiogram.types import Update
from faststream.rabbit import RabbitBroker

from tg_user_forwarder.application.constants import group_route, personal_route
from tg_user_forwarder.application.contracts.update_meta import UpdateMeta
from tg_user_forwarder.settings.models import RabbitSettings


class UpdatesPublisher:
    def __init__(self, broker: RabbitBroker, settings: RabbitSettings) -> None:
        self.personal_publisher = broker.publisher(
            queue=settings.personal_queue,
            routing_key=settings.personal_queue,
        )
        self.group_publisher = broker.publisher(
            queue=settings.group_queue,
            routing_key=settings.group_queue,
        )


    async def publish(self, routing_key: str, update: Update, meta: UpdateMeta) -> None:
        publisher = self.personal_publisher if routing_key == personal_route else self.group_publisher

        payload = {
            "meta": meta.model_dump(mode="json"),
            "update": update.model_dump(mode="json"),
        }

        body = orjson.dumps(payload)
        message = Message(body, content_type="application/json")

        await publisher.publish(message)
