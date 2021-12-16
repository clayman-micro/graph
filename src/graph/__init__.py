import structlog
from fastapi import FastAPI
from starlette_prometheus import PrometheusMiddleware, metrics

from graph.logging import LoggingMiddleware


def init() -> FastAPI:
    """Initialize application."""
    app = FastAPI()
    # app.state.settings = settings

    @app.on_event("startup")
    def on_startup():
        app.logger.info("On startup")

    @app.on_event("shutdown")
    def on_shutdown():
        app.logger.info("On shutdown")

    # Configure metrics
    app.add_middleware(PrometheusMiddleware)
    app.add_route("/-/metrics", metrics)

    # Configure logging
    app.logger = structlog.get_logger("graph")  # type: ignore
    app.add_middleware(LoggingMiddleware)

    return app
