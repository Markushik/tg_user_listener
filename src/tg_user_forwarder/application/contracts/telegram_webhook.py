from __future__ import annotations

from aiogram.types import Update
from pydantic import BaseModel

from tg_user_forwarder.application.contracts.update_meta import UpdateMeta


class TelegramWebhookContract(BaseModel):
    update: Update
    meta: UpdateMeta
