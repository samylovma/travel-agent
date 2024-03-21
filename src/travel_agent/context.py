from typing import Any, Self

from telegram.ext import Application, CallbackContext

from travel_agent.repositories import (
    InviteTokenRepository,
    TravelRepository,
    UserRepository,
)


class Context(CallbackContext):
    def __init__(
        self: Self,
        application: Application,
        chat_id: int | None = None,
        user_id: int | None = None,
    ) -> None:
        super().__init__(application=application, chat_id=chat_id, user_id=user_id)
        self.data: dict[Any, Any] = {}

        self._user_repo: UserRepository | None = None
        self._travel_repo: TravelRepository | None = None
        self._invite_token_repository: InviteTokenRepository | None = None

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
    def invite_token_repo(self: Self) -> InviteTokenRepository:
        if self._invite_token_repository is None:
            self._invite_token_repository = InviteTokenRepository(
                client=self.data["redis_client"]
            )
        return self._invite_token_repository
