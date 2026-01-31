import json
import logging

from fastapi import APIRouter, Header, HTTPException, Request
from aiogram import Bot
from aiogram.types import Update
from dishka.integrations.fastapi import FromDishka, inject

from tg_user_forwarder.settings.models import Settings

router = APIRouter(prefix="/telegram")
logger = logging.getLogger("tg.webhook")



@router.post("/webhook")
@inject
async def telegram_webhook(
    request: Request,
    bot: FromDishka[Bot],
    settings: FromDishka[Settings],
    secret: str | None = Header(default=None, alias="X-Telegram-Bot-Api-Secret-Token"),
):
    if settings.bot.webhook_secret and secret != settings.bot.webhook_secret:
        raise HTTPException(status_code=403, detail="bad secret token")

    payload = await request.json()

    logger.info("keys=%s", list(payload.keys()))
    logger.info("raw=%s", json.dumps(payload, ensure_ascii=False))

    update = Update.model_validate(payload, context={"bot": bot})
    logger.info("update_id=%s", update.update_id)

    return {"ok": True}
