from pydantic import BaseModel, Field


class BotSettings(BaseModel):
    token: str = "123"


class RabbitSettings(BaseModel):
    url: str = "amqp://guest:guest@localhost:5672"
    
    personal_routing_key: str = "tg.bot.user"
    group_routing_key: str = "tg.router.user"


class Settings(BaseModel):
    bot: BotSettings = Field(default_factory=BotSettings)
    rabbit: RabbitSettings = Field(default_factory=RabbitSettings)
    