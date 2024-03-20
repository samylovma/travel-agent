from telegram import Update

from travel_agent.context import Context
from travel_agent.middlewares import middlewares


@middlewares
async def help(update: Update, _: Context) -> None:
    await update.message.reply_text("Мои команды:")
