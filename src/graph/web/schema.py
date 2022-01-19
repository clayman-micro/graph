import strawberry
from strawberry.dataloader import DataLoader
from strawberry.types import Info

from graph.web.definitions import User, load_users


def get_name() -> str:
    return "Strawberry"


def create_dataloader():
    return DataLoader(load_fn=load_users)


@strawberry.type
class Query:
    name: str = strawberry.field(resolver=get_name)

    @strawberry.field
    async def get_user(self, info: Info, id: strawberry.ID) -> User:
        return await info.context["user_loader"].load(id)


schema = strawberry.Schema(query=Query)
