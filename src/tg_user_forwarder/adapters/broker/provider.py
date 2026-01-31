from typing import AsyncIterable

from dishka import Provider, Scope, provide
from faststream.rabbit import RabbitBroker

from tg_user_forwarder.adapters.broker.publisher import UpdatesPublisher

from tg_user_forwarder.settings.models import RabbitSettings

class BrokerProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_broker(self) -> AsyncIterable[RabbitBroker]:
        broker = RabbitBroker(
            "amqp://guest:guest@localhost:5672/",
        )
        await broker.connect()
        yield broker
        await broker.stop()


class UpdatesPublisherProvider(Provider):
    @provide(scope=Scope.APP)
    def updates_publisher(self, broker: RabbitBroker, settings: RabbitSettings) -> UpdatesPublisher:
        return UpdatesPublisher(broker, settings)
            