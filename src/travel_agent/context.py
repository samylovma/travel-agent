from typing import TYPE_CHECKING, Any, Self

from telegram.ext import Application, CallbackContext

from travel_agent.repositories import (
    InviteTokenRepository,
    LocationRepository,
    MapSearchRepository,
    NoteRepository,
    TravelRepository,
    UserRepository,
)

if TYPE_CHECKING:
    from travel_agent.models import User


class Context(CallbackContext):
    def __init__(
        self: Self,
        application: Application,
        chat_id: int | None = None,
        user_id: int | None = None,
    ) -> None:
        super().__init__(application=application, chat_id=chat_id, user_id=user_id)
        self.data: dict[Any, Any] = {}

        self._user: User | None = None

        self._user_repo: UserRepository | None = None
        self._travel_repo: TravelRepository | None = None
        self._note_repo: NoteRepository | None = None
        self._location_repo: LocationRepository | None = None
        self._invite_token_repository: InviteTokenRepository | None = None
        self._map_search_repo: MapSearchRepository | None = None

    @property
    def user_repo(self: Self) -> UserRepository:
        if self._user_repo is None:
            self._user_repo = UserRepository(
                session=self.data["db_session"], auto_commit=True
            )
        return self._user_repo

    @property
    def travel_repo(self: Self) -> TravelRepository:
        if self._travel_repo is None:
            self._travel_repo = TravelRepository(
                session=self.data["db_session"], auto_commit=True
            )
        return self._travel_repo

    @property
    def note_repo(self: Self) -> NoteRepository:
        if self._note_repo is None:
            self._note_repo = NoteRepository(
                session=self.data["db_session"], auto_commit=True
            )
        return self._note_repo

    @property
    def location_repo(self: Self) -> LocationRepository:
        if self._location_repo is None:
            self._location_repo = LocationRepository(
                session=self.data["db_session"], auto_commit=True
            )
        return self._location_repo

    @property
    def invite_token_repo(self: Self) -> InviteTokenRepository:
        if self._invite_token_repository is None:
            self._invite_token_repository = InviteTokenRepository(
                client=self.data["redis_client"]
            )
        return self._invite_token_repository

    @property
    def map_search_repo(self: Self) -> MapSearchRepository:
        if self._map_search_repo is None:
            self._map_search_repo = MapSearchRepository(
                client=self.data["httpx_client"]
            )
        return self._map_search_repo
