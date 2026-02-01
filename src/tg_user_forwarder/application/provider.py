from __future__ import annotations

from dishka import Provider, Scope, provide

from tg_user_forwarder.application.interactors.telegram_webhook import TelegramWebhookInteractor
from tg_user_forwarder.application.services.meta_extractor import MetaExtractorService
from tg_user_forwarder.adapters.broker.publisher import UpdatesPublisher


class ServiceProvider(Provider):
    @provide(scope=Scope.APP)
    def get_meta_extractor_service(self) -> MetaExtractorService:
        return MetaExtractorService()


class InteractorProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_telegram_webhook_interactor(self, updates_publisher: UpdatesPublisher) -> TelegramWebhookInteractor:
        return TelegramWebhookInteractor(updates_publisher=updates_publisher)
