from contextlib import asynccontextmanager
# opentelemetry-instrument --log_level debug python -m uvicorn tg_user_forwarder.main.app:app --host 0.0.0.0 --port 8000

import logging
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from aiogram import Bot

from dishka import AsyncContainer
from dishka.integrations.fastapi import setup_dishka

from tg_user_forwarder.container import get_container
from tg_user_forwarder.presentation.health import router as health_router
from tg_user_forwarder.presentation.telegram import router as telegram_router
from tg_user_forwarder.logging import setup_logging 

setup_logging(logging.INFO) 


def create_app() -> FastAPI:
    container: AsyncContainer = get_container()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.container = container
        yield

        bot = await container.get(Bot)
        await bot.delete_webhook(drop_pending_updates=False)
        await container.close()

    app = FastAPI(lifespan=lifespan, default_response_class=ORJSONResponse)
    
    app.include_router(health_router)
    app.include_router(telegram_router)
    
    setup_dishka(container=container, app=app)
    return app


app = create_app()
