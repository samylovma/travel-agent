import functools

import telegram as tg
from telegram.helpers import mention_html

from travel_agent.context import Context
from travel_agent.types import Callback, CallbackQueryCallback, MessageCallback


def message(function: MessageCallback) -> Callback:
    @functools.wraps(function)
    async def wrapped(update: tg.Update, context: Context) -> None:
        if update.message is None:
            msg = "update.message is None"
            raise ValueError(msg)
        return await function(update.message, context)

    return wrapped


def callback_query(function: CallbackQueryCallback) -> Callback:
    @functools.wraps(function)
    async def wrapped(update: tg.Update, context: Context) -> None:
        if update.callback_query is None:
            msg = "update.callback_query is None"
            raise ValueError(msg)
        return await function(update.callback_query, context)

    return wrapped


def get_mention(user: tg.User) -> str:
    if user.username is not None:
        return f"@{user.username}"
    return mention_html(user_id=user.id, name=user.name)
