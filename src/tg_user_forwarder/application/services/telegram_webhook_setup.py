import logging

from aiogram import Bot

from tg_user_forwarder.settings.models import Settings

logger = logging.getLogger("tg.webhook.setup")


ALLOWED_UPDATES = [
    "message",
    "edited_message",
    "callback_query",
    "chat_member",
    "my_chat_member",
    "chat_join_request",
]


class TelegramWebhookSetupService:
    def __init__(self, bot: Bot, settings: Settings) -> None:
        self._bot = bot
        self._settings = settings

    async def setup(self) -> None:
        bot_settings = self._settings.bot
    
        if not bot_settings.webhook_enabled:
            logger.info("telegram_webhook_setup.disabled")
            return
    
        webhook_url = bot_settings.webhook_url
    
        if not webhook_url.startswith("https://"):
            raise RuntimeError(f"Telegram webhook URL must be HTTPS: {webhook_url}")
    
        webhook_info = await self._bot.get_webhook_info()
    
        logger.info(
            "telegram_webhook_setup.current_state",
            extra={
                "bot_key": bot_settings.bot_key,
                "current_webhook_url": webhook_info.url,
                "target_webhook_url": webhook_url,
            },
        )
    
        await self._bot.set_webhook(
            url=webhook_url,
            secret_token=bot_settings.webhook_secret,
            allowed_updates=ALLOWED_UPDATES,
            drop_pending_updates=False,
            max_connections=40,
        )
    
        logger.info(
            "telegram_webhook_setup.configured",
            extra={
                "bot_key": bot_settings.bot_key,
                "webhook_url": webhook_url,
            },
        )
