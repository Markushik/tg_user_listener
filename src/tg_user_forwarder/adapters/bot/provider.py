from typing import AsyncIterable

from aiogram import Bot
from dishka import Provider, Scope, provide


class BotProvider(Provider):
    @provide(scope=Scope.APP)
    async def bot(
        self,
    ) -> AsyncIterable[Bot]:
        async with Bot(
            token="6996207760:AAEJjYu7fgt3Mmb2Tot6f_jAdXkblWBEuHU",
        ) as bot:
            yield bot
