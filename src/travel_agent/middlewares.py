import functools
import typing

from redis.asyncio import Redis
from telegram import Update

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

        try:
            user = await context.user_repo.get_one_or_none(id=update.effective_user.id)
            if user is None:
                await context.user_repo.add(User(id=update.effective_user.id))

            result = await function(update, context)

        finally:
            await db_session.close()
            await redis_client.aclose()

        return result

    return wrapped
