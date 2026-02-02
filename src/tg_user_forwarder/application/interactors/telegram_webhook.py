from __future__ import annotations

import logging

from aiogram.enums import ChatType

from tg_user_forwarder.adapters.broker.publisher import UpdatesPublisher
from tg_user_forwarder.application.contracts.telegram_webhook import (
    TelegramWebhookContract,
)
from tg_user_forwarder.settings.models import RabbitSettings

logger = logging.getLogger(__name__)


class TelegramWebhookInteractor:
    def __init__(self, updates_publisher: UpdatesPublisher, rabbit_settings: RabbitSettings) -> None:
        self.updates_publisher = updates_publisher
        self.rabbit_settings = rabbit_settings

    async def __call__(self, contract: TelegramWebhookContract) -> None:
        chat_type = contract.meta.chat_type

        if chat_type == ChatType.PRIVATE:
            routing_key = self.rabbit_settings.funnel_routing_key
        elif chat_type in (ChatType.GROUP, ChatType.SUPERGROUP):
            routing_key = self.rabbit_settings.router_routing_key
        else:
            routing_key = self.rabbit_settings.other_routing_key

        await self.updates_publisher.publish(routing_key=routing_key, update=contract.update)
        logger.info("telegram_webhook.published")

