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

        exchange = await broker.declare_exchange(
            RabbitExchange(
                name=settings.exchange,
                type=ExchangeType.DIRECT,
                durable=True,
            )
        )

        bindings = [
            (settings.funnel_queue, settings.funnel_routing_key),
            (settings.router_queue, settings.router_routing_key),
            (settings.other_queue, settings.other_routing_key),
        ]

        for queue_name, routing_key in bindings:
            queue = await broker.declare_queue(RabbitQueue(name=queue_name, durable=True))
            await queue.bind(exchange=exchange, routing_key=routing_key)

        yield broker
        await broker.stop()

class UpdatesPublisherProvider(Provider):
    @provide(scope=Scope.APP)
    def get_updates_publisher(self, broker: RabbitBroker, settings: RabbitSettings) -> UpdatesPublisher:
        return UpdatesPublisher(broker, settings)
