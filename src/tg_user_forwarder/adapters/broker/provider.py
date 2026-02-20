from __future__ import annotations

from typing import AsyncIterable
import logging

from dishka import Provider, Scope, provide
from faststream.rabbit import ExchangeType, RabbitBroker, RabbitExchange, RabbitQueue

from tg_user_forwarder.adapters.broker.publisher import UpdatesPublisher
from tg_user_forwarder.settings.models import RabbitSettings


broker_logger = logging.getLogger("tg.updates.inbound")


class BrokerProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_broker(self, settings: RabbitSettings) -> AsyncIterable[RabbitBroker]:
        broker = RabbitBroker(settings.url, logger=broker_logger)
        await broker.connect()

        exchange = await broker.declare_exchange(
            RabbitExchange(
                name=settings.exchange,
                type=ExchangeType.TOPIC,
                durable=True,
            )
        )

        for queue_name, routing_key in settings.queues.items():
            q = await broker.declare_queue(
                RabbitQueue(
                    name=queue_name,
                    durable=True,
                )
            )
            await q.bind(exchange=exchange, routing_key=routing_key)

        try:
            yield broker
        finally:
            await broker.stop()


class UpdatesPublisherProvider(Provider):
    @provide(scope=Scope.APP)
    def get_updates_publisher(self, broker: RabbitBroker, settings: RabbitSettings) -> UpdatesPublisher:
        return UpdatesPublisher(broker, settings)
