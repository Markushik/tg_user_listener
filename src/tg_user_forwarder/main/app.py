import logging
from contextlib import asynccontextmanager

from dishka import AsyncContainer
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from prometheus_fastapi_instrumentator import Instrumentator

from tg_user_forwarder.container import get_container
from tg_user_forwarder.logging import setup_logging
from tg_user_forwarder.presentation.api.health import router as health_router
from tg_user_forwarder.presentation.api.telegram import router as telegram_router

setup_logging(logging.INFO)


def setup_otel() -> None:
    trace.set_tracer_provider(TracerProvider())


def setup_metrics(app: FastAPI) -> None:
    instrumentator = Instrumentator()
    instrumentator.instrument(app)
    instrumentator.expose(app, endpoint="/metrics")


def create_app() -> FastAPI:
    container: AsyncContainer = get_container()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        setup_otel()
        app.state.container = container
        yield
        await container.close()

    app = FastAPI(lifespan=lifespan)
    setup_dishka(container=container, app=app)

    app.include_router(health_router)
    app.include_router(telegram_router)

    setup_metrics(app)

    return app


app = create_app()