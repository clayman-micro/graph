import click
import structlog
import uvloop

from graph.app import init
from graph.cli.server import server
from graph.logging import configure_logging
from graph.settings import Settings


@click.group()
@click.option("--debug", default=False, is_flag=True)
@click.pass_context
def cli(ctx, debug: bool = False):
    uvloop.install()

    settings = Settings()

    configure_logging(app_name="graph")
    logger = structlog.get_logger("graph")

    ctx.obj["app"] = init(settings=settings, logger=logger)


cli.add_command(server, name="server")


if __name__ == "__main__":
    cli(obj={})
