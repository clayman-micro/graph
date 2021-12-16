import click

from graph.cli.server import server
from graph.logging import configure_logging
from graph.settings import settings


@click.group()
@click.option("--debug", default=False, is_flag=True)
@click.pass_context
def cli(ctx, debug: bool = False):
    configure_logging(app_name="graph")

    ctx.obj["settings"] = settings


cli.add_command(server, name="server")


if __name__ == "__main__":
    cli(obj={})
