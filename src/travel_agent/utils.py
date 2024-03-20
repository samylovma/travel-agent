import functools

from telegram import Update

from travel_agent.context import Context
from travel_agent.types import Callback, CallbackQueryCallback, MessageCallback


def message(function: MessageCallback) -> Callback:
    @functools.wraps(function)
    async def wrapped(update: Update, context: Context) -> None:
        if update.message is None:
            msg = "update.message is None"
            raise ValueError(msg)
        return await function(update.message, context)

    return wrapped


def callback_query(function: CallbackQueryCallback) -> Callback:
    @functools.wraps(function)
    async def wrapped(update: Update, context: Context) -> None:
        if update.callback_query is None:
            msg = "update.callback_query is None"
            raise ValueError(msg)
        return await function(update.callback_query, context)

    return wrapped
