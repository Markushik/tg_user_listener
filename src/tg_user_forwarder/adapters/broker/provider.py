from __future__ import annotations

from typing import AsyncIterable

from dishka import Provider, Scope, provide
from faststream.rabbit import RabbitBroker
from faststream.rabbit.schemas import RabbitExchange, RabbitQueue

from tg_user_forwarder.adapters.broker.publisher import UpdatesPublisher
from tg_user_forwarder.settings.models import RabbitSettings

class BrokerProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_broker(self, settings: RabbitSettings) -> AsyncIterable[RabbitBroker]:
        broker = RabbitBroker(settings.url)
        await broker.connect()

        await broker.declare_queue(
            RabbitQueue(name=settings.personal_queue, durable=True, routing_key=settings.personal_queue)
        )

        await broker.declare_queue(
            RabbitQueue(name=settings.group_queue, durable=True, routing_key=settings.group_queue)
        )

        yield broker
        await broker.stop()

class UpdatesPublisherProvider(Provider):
    @provide(scope=Scope.APP)
    def get_updates_publisher(self, broker: RabbitBroker, settings: RabbitSettings) -> UpdatesPublisher:
        return UpdatesPublisher(broker, settings)
