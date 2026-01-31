import os

from pydantic import BaseModel, Field


class BotSettings(BaseModel):
    token: str = "6996207760:AAEJjYu7fgt3Mmb2Tot6f_jAdXkblWBEuHU"
    
    webhook_base_url: str = Field(default_factory=lambda: os.getenv("WEBHOOK_BASE_URL", "https://example.com"))
    webhook_path: str = Field(default_factory=lambda: os.getenv("WEBHOOK_PATH", "/telegram/webhook"))
    webhook_secret: str = Field(default_factory=lambda: os.getenv("WEBHOOK_SECRET", "my-secret"))


class RabbitSettings(BaseModel):
    url: str = "amqp://guest:guest@localhost:5672"
    
    personal_routing_key: str = "tg.bot.user"
    group_routing_key: str = "tg.router.user"


class Settings(BaseModel):
    bot: BotSettings = Field(default_factory=BotSettings)
    rabbit: RabbitSettings = Field(default_factory=RabbitSettings)
    