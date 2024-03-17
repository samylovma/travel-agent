from telegram import Update
from telegram.ext import ContextTypes


async def echo(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(update.message.text)
