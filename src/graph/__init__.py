import aio_pika
import aiojobs
import structlog
from fastapi import FastAPI
from starlette_prometheus import PrometheusMiddleware, metrics
from strawberry.fastapi import GraphQLRouter

from graph.events import event_consumer
from graph.logging import LoggingMiddleware
from graph.settings import settings
from graph.web.schema import schema


def setup_rabbitmq(app: FastAPI) -> None:
    """Setup rabbitmq connection."""
    app.state.rabbitmq = None
    app.state.rabbitmq_channel = None

    @app.on_event("startup")
    async def on_startup():
        app.logger.info("On startup")

        try:
            app.state.rabbitmq = await aio_pika.connect(settings.rabbitmq_dsn)
            app.state.rabbitmq_channel = await app.state.rabbitmq.channel()
            await app.state.rabbitmq_channel.set_qos(prefetch_count=1)
        except ConnectionError as exc:
            app.logger.error("RabbitMQ connection error")

            raise exc

    @app.on_event("shutdown")
    async def on_shutdown():
        app.logger.info("On shutdown")

        await app.state.rabbitmq.close()


def setup_scheduler(app: FastAPI) -> None:
    """Setup background tasks scheduler."""
    app.state.scheduler = None

    @app.on_event("startup")
    async def on_startup():
        app.state.scheduler = await aiojobs.create_scheduler()
        await app.state.scheduler.spawn(event_consumer(app))

    @app.on_event("shutdown")
    async def on_shutdown():
        await app.state.scheduler.close()


def init() -> FastAPI:
    """Initialize application."""
    app = FastAPI()
    app.state.settings = settings

    # Configure rabbitmq
    setup_rabbitmq(app)

    # Configure background tasks scheduler
    setup_scheduler(app)

    # Configure metrics
    app.add_middleware(PrometheusMiddleware)
    app.add_route("/-/metrics", metrics)

    # Configure logging
    app.logger = structlog.get_logger("graph")  # type: ignore
    app.add_middleware(LoggingMiddleware)

    graphql_app = GraphQLRouter(schema)
    app.include_router(graphql_app, prefix="/graphql")

    return app
