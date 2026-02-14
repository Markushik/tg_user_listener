import logging
from contextlib import asynccontextmanager

from dishka import AsyncContainer
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from prometheus_fastapi_instrumentator import Instrumentator

from tg_user_forwarder.container import get_container
from tg_user_forwarder.logging import setup_logging
from tg_user_forwarder.presentation.api.health import router as health_router
from tg_user_forwarder.presentation.api.telegram import router as telegram_router

setup_logging(logging.INFO)

def setup_metrics(app: FastAPI) -> None:
    instrumentator = Instrumentator()

    instrumentator.instrument(app)
    instrumentator.expose(app, endpoint="/metrics")


def create_app() -> FastAPI:
    container: AsyncContainer = get_container()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.container = container
        yield
        await container.close()

    app = FastAPI(lifespan=lifespan, default_response_class=ORJSONResponse)
    setup_dishka(container=container, app=app)

    app.include_router(health_router)
    app.include_router(telegram_router)

    return app

app = create_app()
