from __future__ import annotations

import logging
from typing import AsyncIterable

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

        main_exchange = await broker.declare_exchange(
            RabbitExchange(
                name=settings.exchange,
                type=ExchangeType.TOPIC,
                durable=True,
            )
        )

        retry_exchange = await broker.declare_exchange(
            RabbitExchange(
                name=settings.retry_exchange,
                type=ExchangeType.TOPIC,
                durable=True,
            )
        )

        for queue_name, routing_key in settings.queues.items():
            # main queue with DLX to retry exchange
            q = await broker.declare_queue(
                RabbitQueue(
                    name=queue_name,
                    durable=True,
                    arguments={
                        "x-dead-letter-exchange": settings.retry_exchange,
                        "x-dead-letter-routing-key": f"{routing_key}{settings.retry_routing_key_suffix}",
                    },
                )
            )
            await q.bind(exchange=main_exchange, routing_key=routing_key)

            # retry queue with TTL and return to main exchange
            retry_queue_name = f"{queue_name}{settings.retry_queue_suffix}"
            retry_routing_key = f"{routing_key}{settings.retry_routing_key_suffix}"

            retry_q = await broker.declare_queue(
                RabbitQueue(
                    name=retry_queue_name,
                    durable=True,
                    arguments={
                        "x-message-ttl": settings.retry_ttl_ms,
                        "x-dead-letter-exchange": settings.exchange,
                        "x-dead-letter-routing-key": routing_key,
                    },
                )
            )
            await retry_q.bind(exchange=retry_exchange, routing_key=retry_routing_key)

        try:
            yield broker
        finally:
            await broker.stop()


class UpdatesPublisherProvider(Provider):
    @provide(scope=Scope.APP)
    def get_updates_publisher(self, broker: RabbitBroker, settings: RabbitSettings) -> UpdatesPublisher:
        return UpdatesPublisher(broker, settings)