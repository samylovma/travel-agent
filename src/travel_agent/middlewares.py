import functools
import typing

import httpx
from fluent_compiler.bundle import FluentBundle
from redis.asyncio import Redis
from telegram import Update

from travel_agent.constants import LOCALES_DIR
from travel_agent.context import Context
from travel_agent.models import User
from travel_agent.types import Callback

if typing.TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


def middlewares(function: Callback) -> Callback:
    @functools.wraps(function)
    async def wrapped(update: Update, context: Context) -> None:
        db_session_factory = context.bot_data["db_session_factory"]
        db_session: "AsyncSession" = db_session_factory()
        context.data["db_session"] = db_session

        redis_pool = context.bot_data["redis_pool"]
        redis_client = Redis.from_pool(redis_pool)
        context.data["redis_client"] = redis_client

        httpx_client = httpx.AsyncClient()
        context.data["httpx_client"] = httpx_client

        # TODO: FluentBundle.from_files reads files every time. We should read it once.
        l10n = FluentBundle.from_files("ru", [LOCALES_DIR / "ru.ftl"])
        context.data["l10n"] = l10n

        try:
            user = await context.user_repo.get_one_or_none(id=update.effective_user.id)
            if user is None:
                await context.user_repo.add(User(id=update.effective_user.id))

            result = await function(update, context)

        finally:
            await db_session.close()
            await redis_client.aclose()
            await httpx_client.aclose()

        return result

    return wrapped
