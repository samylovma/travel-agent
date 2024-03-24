from telegram import Message

from travel_agent.context import Context
from travel_agent.middlewares import middlewares
from travel_agent.utils import message_callback


@middlewares
@message_callback
async def help(message: Message, _: Context) -> None:
    await message.reply_text("Мои команды:")
