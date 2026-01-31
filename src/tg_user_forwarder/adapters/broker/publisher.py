from __future__ import annotations

from typing import Any

from aiogram.enums import ChatType
from faststream.rabbit import RabbitBroker

from tg_user_forwarder.settings.models import RabbitSettings


class UpdatesPublisher:
    def __init__(self, broker: RabbitBroker, settings: RabbitSettings) -> None:
        self.personal_publisher = broker.publisher(routing_key=settings.personal_routing_key)
        self.group_publisher = broker.publisher(routing_key=settings.group_routing_key)

    def pick_publisher(self, chat_type: ChatType):
        if chat_type == ChatType.PRIVATE:
            return self.personal_publisher
        return self.group_publisher

    async def publish(self, update: Any, chat_type: ChatType) -> None:
        publisher = self.pick_publisher(chat_type)
        await publisher.publish(update)
