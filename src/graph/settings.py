from typing import Optional

from pydantic import AnyUrl, BaseSettings, Field


class RabbitMQDSN(AnyUrl):
    allowed_schemes = {"amqp"}
    user_required = True


class Settings(BaseSettings):
    debug: bool = False
    rabbitmq_dsn: RabbitMQDSN = Field(default="amqp://rabbit:rabbit@localhost:5672/")
    sentry_dsn: Optional[AnyUrl] = None


settings = Settings()
