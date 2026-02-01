from dishka import AsyncContainer, make_async_container

from tg_user_forwarder.adapters.broker.provider import BrokerProvider, UpdatesPublisherProvider
from tg_user_forwarder.adapters.bot.provider import BotProvider
from tg_user_forwarder.settings.provider import SettingsProvider
from tg_user_forwarder.application.provider import ServiceProvider, InteractorProvider


def get_container() -> AsyncContainer:
    container = make_async_container(
        *[
            SettingsProvider(),
            BrokerProvider(),
            UpdatesPublisherProvider(),
            BotProvider(),
            ServiceProvider(),
            InteractorProvider(),
        ]
    )
    return container
