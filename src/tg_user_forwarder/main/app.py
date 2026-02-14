import logging
from contextlib import asynccontextmanager

from aiogram import Bot
from dishka import AsyncContainer
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from tg_user_forwarder.container import get_container
from tg_user_forwarder.logging import setup_logging
from tg_user_forwarder.presentation.health import router as health_router
from tg_user_forwarder.presentation.telegram import router as telegram_router
from tg_user_forwarder.settings.models import Settings

setup_logging(logging.INFO)

# poetry run ruff check src/tg_user_forwarder --fix

def create_app() -> FastAPI:
    container: AsyncContainer = get_container()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.container = container

        # bot = await container.get(Bot)
        # settings = await container.get(Settings)

        # webhook_url = f"{settings.bot.webhook_base_url}{settings.bot.webhook_path}"
        # await bot.set_webhook(
        #     webhook_url,
        #     secret_token=settings.bot.webhook_secret,
        #     drop_pending_updates=False,
        # )
        yield

        # TODO: EMERGENCY -- DELETE THIS WHEN GO TO THE PROD!!!!!!!
        # await bot.delete_webhook(drop_pending_updates=False)
        await container.close()

    app = FastAPI(lifespan=lifespan, default_response_class=ORJSONResponse)
    setup_dishka(container=container, app=app)

    app.include_router(health_router)
    app.include_router(telegram_router)

    return app

app = create_app()
