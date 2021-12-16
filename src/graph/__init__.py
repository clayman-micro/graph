import aio_pika
import structlog
from fastapi import FastAPI
from starlette_prometheus import PrometheusMiddleware, metrics

from graph.logging import LoggingMiddleware
from graph.settings import settings


def init() -> FastAPI:
    """Initialize application."""
    app = FastAPI()
    app.state.settings = settings

    # Configure rabbitmq
    app.state.rabbitmq = None

    # Configure metrics
    app.add_middleware(PrometheusMiddleware)
    app.add_route("/-/metrics", metrics)

    # Configure logging
    app.logger = structlog.get_logger("graph")  # type: ignore
    app.add_middleware(LoggingMiddleware)

    @app.on_event("startup")
    async def on_startup():
        app.logger.info("On startup")

        try:
            app.state.rabbitmq = await aio_pika.connect(settings.rabbitmq_dsn)
        except ConnectionError as exc:
            app.logger.error("RabbitMQ connection error")

            raise exc

    @app.on_event("shutdown")
    async def on_shutdown():
        app.logger.info("On shutdown")

        await app.state.rabbitmq.close()

    return app
