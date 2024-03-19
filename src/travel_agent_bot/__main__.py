import logging
from os import getenv

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler, MessageHandler, filters

from .callbacks.settings import settings_age, settings_age_answered, settings_menu, settings_sex_female, settings_sex_male, settings_sex_menu, back_to_settings_menu
from .callbacks.help import help
from .callbacks.start import start
from .models import Base
from .context import Context


async def post_init(application: Application) -> None:
    engine: AsyncEngine = application.bot_data["db_engine"]
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("telegram").setLevel(logging.DEBUG)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    application = (
        Application.builder()
        .token(getenv("TELEGRAM_TOKEN"))
        .post_init(post_init)
        .context_types(ContextTypes(Context))
        .build()
    )

    application.bot_data["db_engine"] = create_async_engine(getenv("DB_URL"))
    application.bot_data["db_session_factory"] = async_sessionmaker(application.bot_data["db_engine"])

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))

    application.add_handler(CommandHandler("settings", settings_menu))
    application.add_handler(CallbackQueryHandler(settings_sex_menu, "^settings_sex$"))
    application.add_handler(CallbackQueryHandler(settings_sex_male, "^settings_sex_male$"))
    application.add_handler(CallbackQueryHandler(settings_sex_female, "^settings_sex_female$"))
    application.add_handler(CallbackQueryHandler(back_to_settings_menu, "^settings_sex_back$"))

    application.add_handler(
        ConversationHandler(
            entry_points=[CallbackQueryHandler(settings_age, "^settings_age$")],
            states={1: [MessageHandler(filters.TEXT, settings_age_answered)]},
            fallbacks=[],
        )
    )

    application.run_polling()


if __name__ == "__main__":
    main()
