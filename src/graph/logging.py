import socket
from logging.config import dictConfig
from typing import Callable

import pkg_resources
import structlog
import ujson
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.types import EventDict, WrappedLogger


def add_hostname() -> Callable[[WrappedLogger, str, EventDict], EventDict]:
    hostname = socket.gethostname()

    def processor(logger: WrappedLogger, name: str, event_dict: EventDict) -> EventDict:
        event_dict["hostname"] = hostname

        return event_dict

    return processor


def add_app_name(app_name: str) -> Callable[[WrappedLogger, str, EventDict], EventDict]:
    distribution = pkg_resources.get_distribution(app_name)

    def processor(logger: WrappedLogger, name: str, event_dict: EventDict) -> EventDict:
        event_dict["app_name"] = distribution.project_name
        event_dict["version"] = distribution.version

        return event_dict

    return processor


def configure_logging(app_name: str) -> None:
    """Configure application logging.

    Args:
        app_name: The name of the application.
    """
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "()": "structlog.stdlib.ProcessorFormatter",
                    "processors": [
                        add_hostname(),
                        add_app_name(app_name),
                        structlog.stdlib.add_log_level,
                        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                        structlog.processors.format_exc_info,
                        structlog.processors.TimeStamper(fmt="iso"),
                        structlog.processors.JSONRenderer(serializer=ujson.dumps),
                    ],
                }
            },
            "handlers": {
                "default": {"formatter": "default", "class": "logging.StreamHandler", "stream": "ext://sys.stdout"},
                "error": {"formatter": "default", "class": "logging.StreamHandler", "stream": "ext://sys.stderr"},
            },
            "loggers": {
                app_name: {"handlers": ["default"], "level": "INFO", "propagate": False},
                "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
                "uvicorn.error": {"handlers": ["error"], "level": "INFO", "propagate": False},
            },
        }
    )

    structlog.configure(
        cache_logger_on_first_use=True,
        processors=[structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
    )


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request.state.logger = request.app.logger.bind()
        response = await call_next(request)
        request.state.logger.info(
            f"{request.method} {request.url.path} {response.status_code}",
            request={"method": request.method, "url": request.url.path},
            response={"status_code": response.status_code},
        )
        return response
