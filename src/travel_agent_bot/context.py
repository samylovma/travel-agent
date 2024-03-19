from typing import Self, Any

from telegram.ext import CallbackContext, Application

from .repositories.user import UserRepository


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

    @property
    def user_repo(self) -> UserRepository:
        if self._user_repo is None:
            self._user_repo = UserRepository(session=self.data["db_session"])
        return self._user_repo
