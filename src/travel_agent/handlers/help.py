from telegram import Message
from telegram.ext import BaseHandler, CommandHandler

from travel_agent.context import Context
from travel_agent.middlewares import middlewares
from travel_agent.utils import message_callback


def create_handlers() -> list[BaseHandler]:
    return [CommandHandler("help", help_callback)]


@middlewares
@message_callback
async def help_callback(message: Message, _: Context) -> None:
    await message.reply_text(
        "<b>Мои команды</b>\n\n"
        "/settings -- настройки профиля.\n"
        "/travels -- меню путешествий.\n"
        "/newtravel -- создать путешествие."
    )
