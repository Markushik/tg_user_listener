from __future__ import annotations

import logging

from aiogram import Bot
from aiogram.types import Update
from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import ValidationError

from tg_user_forwarder.application.contracts.telegram_webhook import (
    TelegramWebhookContract,
)
from tg_user_forwarder.application.interactors.telegram_webhook import (
    TelegramWebhookInteractor,
)
from tg_user_forwarder.application.services.meta_extractor import MetaExtractorService
from tg_user_forwarder.logging import set_context
from tg_user_forwarder.settings.models import Settings

router = APIRouter(prefix="/telegram")
logger = logging.getLogger("tg.webhook")


@router.post("/webhook")
@inject
async def telegram_webhook(
    request: Request,
    bot: FromDishka[Bot],
    settings: FromDishka[Settings],
    meta_extractor: FromDishka[MetaExtractorService],
    telegram_webhook: FromDishka[TelegramWebhookInteractor],
    secret: str | None = Header(default=None, alias="X-Telegram-Bot-Api-Secret-Token"),
) -> dict[str, bool]:
    webhook_secret = settings.bot.webhook_secret
    if webhook_secret and secret != webhook_secret:
        raise HTTPException(status_code=403, detail="bad secret token")

    body = await request.body()

    try:
        update = Update.model_validate_json(body, context={"bot": bot})
    except ValidationError:
        raise HTTPException(status_code=400, detail="invalid json")

    meta = meta_extractor.extract(update)
    set_context(update_id=meta.update_id, user_id=meta.user_id, chat_id=meta.chat_id)

    logger.info("telegram_webhook.received")

    contract = TelegramWebhookContract(update=update, meta=meta)
    await telegram_webhook(contract)

    return {"ok": True}
