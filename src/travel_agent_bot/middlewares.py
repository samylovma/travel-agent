from collections.abc import Callable, Coroutine
import functools

from telegram import Update

from .models import User
from .context import Context


def middlewares[YT, ST, RT](
    function: Callable[[Update, Context], Coroutine[YT, ST, RT]],
) -> Callable[[Update, Context], Coroutine[YT, ST, RT]]:
    @functools.wraps(function)
    async def wrapped(update: Update, context: Context) -> None:
        async with context.bot_data["db_session_factory"]() as session:
            context.data["db_session"] = session
            user = await context.user_repo.get(update.effective_user.id)
            if user is None:
                user = await context.user_repo.create(User(id=update.effective_user.id))
            context.data["user"] = user
            return await function(update, context)

    return wrapped
