from typing import AsyncIterable

from aiogram import Bot
from aiogram.types import BotCommand
from aiogram.types import BotCommandScopeAllGroupChats, BotCommandScopeAllPrivateChats
from dishka import Provider, Scope, provide

from tg_user_forwarder.settings.models import Settings


class BotProvider(Provider):
    @provide(scope=Scope.APP)
    async def bot(self, settings: Settings) -> AsyncIterable[Bot]:
        async with Bot(token=settings.bot.token) as bot:
            commands = [
                BotCommand(command="start", description="— запустить бота"),
            ]

            await bot.set_my_commands(commands, scope=BotCommandScopeAllPrivateChats())
            await bot.set_my_commands([], scope=BotCommandScopeAllGroupChats())

            yield bot
