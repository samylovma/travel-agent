import functools

from telegram import Update

from travel_agent.context import Context
from travel_agent.types import Callback


def middlewares(function: Callback) -> Callback:
    @functools.wraps(function)
    async def wrapped(update: Update, context: Context) -> None:
        async with context.bot_data["db_session_factory"]() as session:
            context.data["db_session"] = session

            user, _ = await context.user_repo.get_or_upsert(id=update.effective_user.id)
            context.data["user"] = user

            return await function(update, context)

    return wrapped
