from telegram import Update

from travel_agent.context import Context
from travel_agent.middlewares import middlewares


@middlewares
async def start(update: Update, _: Context) -> None:
    await update.message.reply_text(
        "Здравствуй, Путник!\n"
        "Я — Тревел Агент. Cтрашно звучит, не правда ли? Сейчас всё расскажу!\n"
        "Я могу взять на себя твои рутинные дела во время путешествия.\n"
        "Если хочешь рассказать о себе больше, жми /settings.\n"
        "/help — список команд.\n"
    )
