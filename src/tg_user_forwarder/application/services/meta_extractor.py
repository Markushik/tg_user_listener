from __future__ import annotations

from typing import Optional

from aiogram.enums import ChatType, UpdateType
from aiogram.types import Update

from tg_user_forwarder.application.contracts.update_meta import UpdateMeta


class MetaExtractorService:
    def extract(self, update: Update) -> UpdateMeta:
        event_type = UpdateType(update.event_type)
        event_object = update.event

        chat_id: Optional[int] = None
        chat_type: Optional[ChatType] = None
        user_id: Optional[int] = None

        chat = getattr(event_object, "chat", None)
        if not chat and hasattr(event_object, "message"):
            message = getattr(event_object, "message", None)
            chat = getattr(message, "chat", None) if message else None

        if chat:
            chat_id = chat.id
            chat_type = chat.type

        from_user = getattr(event_object, "from_user", None) or getattr(event_object, "user", None)
        if from_user:
            user_id = from_user.id

        return UpdateMeta(
            update_id=update.update_id,
            event_type=event_type,
            chat_type=chat_type,
            chat_id=chat_id,
            user_id=user_id,
        )
