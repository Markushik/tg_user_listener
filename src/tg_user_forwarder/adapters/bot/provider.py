from typing import AsyncIterable

from aiogram import Bot
from dishka import Provider, Scope, provide

from aiogram.types.bot_command import BotCommand
from aiogram.types import BotCommandScopeAllPrivateChats, BotCommandScopeAllGroupChats

class BotProvider(Provider):
    @provide(scope=Scope.APP)
    async def bot(
        self,
    ) -> AsyncIterable[Bot]:
        async with Bot(
            token="6996207760:AAEQbsRpJCuWp7bKAfk24t7RecPqskBLpZQ",
        ) as bot:
            commands = [
                BotCommand(command="start", description="— запустить бота"),
            ]

            await bot.set_my_commands(commands, scope=BotCommandScopeAllPrivateChats())
            await bot.set_my_commands([], scope=BotCommandScopeAllGroupChats())
            
            yield bot
