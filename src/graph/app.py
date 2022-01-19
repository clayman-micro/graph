from logging import Logger

from aiohttp import web
from strawberry.aiohttp.views import GraphQLView

from graph.settings import Settings
from graph.web.schema import create_dataloader, schema


class GraphQL(GraphQLView):
    async def get_context(self, request: web.Request, response: web.StreamResponse) -> object:
        return {"user_loader": create_dataloader()}


def init(settings: Settings, logger: Logger) -> web.Application:
    app = web.Application()

    app["logger"] = logger
    app["settings"] = settings

    app.router.add_route("*", "/graphql", GraphQL(schema=schema))

    app["logger"].info("Initialize application")

    return app
