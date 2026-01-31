from dishka import AsyncContainer, make_async_container

from tg_user_forwarder.adapters.broker.provider import BrokerProvider
from tg_user_forwarder.adapters.bot.provider import BotProvider
from tg_user_forwarder.settings.provider import SettingsProvider


def get_container() -> AsyncContainer:
    container = make_async_container(
        *[
            SettingsProvider(),
            BrokerProvider(),
            BotProvider(),
        ]
    )
    return container