from dishka import provide, Provider, Scope

from tg_user_forwarder.settings.models import (
    BotSettings,
    RabbitSettings,
    Settings,
)


class SettingsProvider(Provider):
    scope = Scope.APP

    def __init__(self):
        super().__init__()
        self.settings = Settings()

    @provide
    def get_config(self) -> Settings:
        return self.settings

    @provide
    def get_bot_config(self) -> BotSettings:
        return self.settings.bot

    @provide
    def get_rabbit_config(self) -> RabbitSettings:
        return self.settings.rabbit
        