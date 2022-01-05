import strawberry
from strawberry.dataloader import DataLoader

from graph.web.definitions import User, load_users


def get_name() -> str:
    return "Strawberry"


loader = DataLoader(load_fn=load_users)


@strawberry.type
class Query:
    name: str = strawberry.field(resolver=get_name)

    @strawberry.field
    async def get_user(self, id: strawberry.ID) -> User:
        return await loader.load(id)


schema = strawberry.Schema(query=Query)
