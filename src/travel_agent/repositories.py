import secrets
import typing
from dataclasses import dataclass
from datetime import timedelta

import httpx
from advanced_alchemy import SQLAlchemyAsyncRepository
from redis.asyncio import Redis
from sqlalchemy import insert

from travel_agent.models import Location, Note, Travel, User, user_to_travel_table


class UserRepository(SQLAlchemyAsyncRepository[User]):
    model_type = User


class TravelRepository(SQLAlchemyAsyncRepository[Travel]):
    model_type = Travel

    async def add_user_to(self: typing.Self, travel_id: int, user_id: int) -> None:
        stmt = insert(user_to_travel_table).values(user_id=user_id, travel_id=travel_id)
        await self.session.execute(stmt)
        await self._flush_or_commit(auto_commit=None)


class NoteRepository(SQLAlchemyAsyncRepository[Note]):
    model_type = Note


class LocationRepository(SQLAlchemyAsyncRepository[Location]):
    model_type = Location


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
        result: int | None = await self.client.get(name=invite_token)
        if result is not None:
            result = int(result)
        return result


@dataclass
class Place:
    lat: float
    lon: float
    name: str
    address: str


class MapSearchRepository:
    def __init__(self: typing.Self, client: httpx.AsyncClient) -> None:
        self.client = client

    async def search(self: typing.Self, query: str) -> list[Place]:
        response = await self.client.get(
            "https://nominatim.openstreetmap.org/search",
            params={"format": "jsonv2", "q": query},
            headers={"Accept-Language": "ru"},
        )
        if not response.is_success:
            raise
        data = response.json()
        return [
            Place(
                lat=float(place["lat"]),
                lon=float(place["lon"]),
                name=place["name"],
                address=place["display_name"],
            )
            for place in data
        ]


class RouteRepository:
    def __init__(self: typing.Self, client: httpx.AsyncClient) -> None:
        self.client = client

    async def create_car_route(
        self: typing.Self, *args: tuple[float, float]
    ) -> list[tuple[float, float]]:
        coordinates = ";".join([f"{arg[0]},{arg[1]}" for arg in args])
        response = await self.client.get(
            f"https://router.project-osrm.org/route/v1/car/{coordinates}.json",
            params={
                "geometries": "geojson",
                "overview": "simplified",
            },
        )
        if not response.is_success:
            raise
        return response.json()["routes"][0]["geometry"]["coordinates"]
