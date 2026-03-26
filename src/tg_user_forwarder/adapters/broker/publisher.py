from __future__ import annotations

from aiogram.enums import ChatType
from aiogram.types import Update
from faststream.rabbit import RabbitBroker
from opentelemetry.propagate import inject

from tg_user_forwarder.settings.models import RabbitSettings


class UpdatesPublisher:
    def __init__(self, broker: RabbitBroker, settings: RabbitSettings) -> None:
        self.broker = broker
        self.exchange = settings.exchange
        self.audience = settings.audience

    def _choose_scope(self, chat_type: ChatType | None) -> str:
        if chat_type == ChatType.PRIVATE:
            return "private"
        if chat_type in (ChatType.GROUP, ChatType.SUPERGROUP):
            return "group"
        return "other"

    async def publish(self, update: Update, chat_type: ChatType | None) -> None:
        headers: dict = {} # otel headers
        inject(headers)

        scope = self._choose_scope(chat_type)
        routing_key = f"updates.{self.audience}.{scope}"

        await self.broker.publish(
            message=update,
            exchange=self.exchange,
            routing_key=routing_key,
            headers=headers,
        )