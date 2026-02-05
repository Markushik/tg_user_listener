from __future__ import annotations

import logging

from tg_user_forwarder.adapters.broker.publisher import UpdatesPublisher
from tg_user_forwarder.application.contracts.telegram_webhook import TelegramWebhookContract

logger = logging.getLogger(__name__)


class TelegramWebhookInteractor:
    def __init__(self, updates_publisher: UpdatesPublisher) -> None:
        self.updates_publisher = updates_publisher

    async def __call__(self, contract: TelegramWebhookContract) -> None:
        await self.updates_publisher.publish(update=contract.update, chat_type=contract.meta.chat_type)
        logger.info("telegram_webhook.published")
