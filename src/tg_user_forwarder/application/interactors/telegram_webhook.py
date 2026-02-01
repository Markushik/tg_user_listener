from __future__ import annotations

import logging

from aiogram.enums import ChatType

from tg_user_forwarder.application.constants import group_route, other_route, personal_route
from tg_user_forwarder.application.contracts.telegram_webhook import TelegramWebhookContract
from tg_user_forwarder.adapters.broker.publisher import UpdatesPublisher

logger = logging.getLogger(__name__)


class TelegramWebhookInteractor:
    def __init__(self, updates_publisher: UpdatesPublisher) -> None:
        self.updates_publisher = updates_publisher

    async def __call__(self, contract: TelegramWebhookContract) -> None:
        update = contract.update
        meta = contract.meta

        routing_key = other_route
        if meta.chat_type == ChatType.PRIVATE:
            routing_key = personal_route
        elif meta.chat_type in (ChatType.GROUP, ChatType.SUPERGROUP):
            routing_key = group_route

        await self.updates_publisher.publish(routing_key=routing_key, update=update)
        logger.info("telegram_webhook.published")
