from collections.abc import Callable, Coroutine
from typing import TypeAlias, TypeVar

from telegram import CallbackQuery, Message, Update

from travel_agent.context import Context

YT = TypeVar("YT")
ST = TypeVar("ST")
RT = TypeVar("RT")
Callback: TypeAlias = Callable[[Update, Context], Coroutine[YT, ST, RT]]
MessageCallback: TypeAlias = Callable[[Message, Context], Coroutine[YT, ST, RT]]
CallbackQueryCallback: TypeAlias = Callable[[CallbackQuery, Context], Coroutine[YT, ST, RT]]
