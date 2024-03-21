import secrets
import typing
from datetime import timedelta

from advanced_alchemy import SQLAlchemyAsyncRepository
from redis.asyncio import Redis
from sqlalchemy import insert

from travel_agent.models import Travel, User, user_to_travel_table


class UserRepository(SQLAlchemyAsyncRepository[User]):
    model_type = User


class TravelRepository(SQLAlchemyAsyncRepository[Travel]):
    model_type = Travel

    async def add_user_to(self: typing.Self, travel_id: int, user_id: int) -> None:
        stmt = insert(user_to_travel_table).values(user_id=user_id, travel_id=travel_id)
        await self.session.execute(stmt)
        await self._flush_or_commit(auto_commit=None)


class InviteTokenRepository:
    def __init__(self: typing.Self, client: Redis) -> None:
        self.client = client

    async def create(self: typing.Self, travel_id: int) -> str:
        invite_token: str = secrets.token_urlsafe(6)
        await self.client.set(
            name=invite_token, value=travel_id, ex=timedelta(hours=24)
        )
        return invite_token

    async def get_travel_id(self: typing.Self, invite_token: str) -> int | None:
        result = await self.client.get(name=invite_token)
        if result is not None:
            result = int(result)
        return result