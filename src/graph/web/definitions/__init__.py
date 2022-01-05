from typing import List

import strawberry


@strawberry.type
class User:
    id: strawberry.ID


async def load_users(keys: List[int]) -> List[User]:
    return [User(id=key) for key in keys]
