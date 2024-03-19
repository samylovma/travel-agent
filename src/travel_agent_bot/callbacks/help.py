from telegram import Update

from ..context import Context
from ..middlewares import middlewares


@middlewares
async def help(update: Update, _: Context) -> None:
    await update.message.reply_text("Мои команды:")
