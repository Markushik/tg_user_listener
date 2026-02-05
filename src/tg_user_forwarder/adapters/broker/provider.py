from __future__ import annotations

from typing import AsyncIterable

from dishka import Provider, Scope, provide
from faststream.rabbit import ExchangeType, RabbitBroker, RabbitExchange, RabbitQueue

from tg_user_forwarder.adapters.broker.publisher import UpdatesPublisher
from tg_user_forwarder.settings.models import RabbitSettings


class BrokerProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_broker(self, settings: RabbitSettings) -> AsyncIterable[RabbitBroker]:
        broker = RabbitBroker(settings.url)
        await broker.connect()

        await broker.declare_exchange(
            RabbitExchange(
                name=settings.exchange,
                type=ExchangeType.TOPIC,
                durable=True,
            )
        )

        try:
            yield broker
        finally:
            await broker.stop()

class UpdatesPublisherProvider(Provider):
    @provide(scope=Scope.APP)
    def get_updates_publisher(self, broker: RabbitBroker, settings: RabbitSettings) -> UpdatesPublisher:
        return UpdatesPublisher(broker, settings)
