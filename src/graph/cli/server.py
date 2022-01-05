import socket

import click
import uvicorn  # type: ignore


def get_address(default: str = "127.0.0.1") -> str:
    try:
        ip_address = socket.gethostbyname(socket.gethostname())
    except socket.gaierror:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 1))
            ip_address = s.getsockname()[0]
        except socket.gaierror:
            ip_address = default
        finally:
            s.close()

    return ip_address


@click.group()
@click.pass_context
def server(ctx):
    pass


@server.command()
@click.option("--host", default=None, help="Specify application host")
@click.option("--port", default=5000, help="Specify application port")
@click.pass_context
def run(ctx, host, port):
    try:
        port = int(port)

        if port < 1024 and port > 65535:
            raise RuntimeError("Port should be from 1024 to 65535")
    except ValueError:
        raise RuntimeError("Port should be numeric")

    if not host:
        host = "127.0.0.1"
        address = "127.0.0.1"
    else:
        address = get_address()

    uvicorn.run(
        "graph:app", host=address, port=port, access_log=False, log_level="info", log_config=None, loop="uvloop",
    )
