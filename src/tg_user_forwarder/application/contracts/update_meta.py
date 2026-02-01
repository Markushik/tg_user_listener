from __future__ import annotations

from typing import Optional
from pydantic import BaseModel
from aiogram.enums import ChatType, UpdateType


class UpdateMeta(BaseModel):
    update_id: int
    event_type: UpdateType
    chat_type: Optional[ChatType] = None
    chat_id: Optional[int] = None
    user_id: Optional[int] = None
