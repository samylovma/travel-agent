import logging
import os
import typing

from advanced_alchemy.base import orm_registry
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    Defaults,
    MessageHandler,
    filters,
)
from travel_agent_bot.callbacks.settings import back_to_settings_menu

from travel_agent.callbacks import travel
from travel_agent.callbacks.help import help
from travel_agent.callbacks.settings import (
    settings_age,
    settings_age_answered,
    settings_menu,
    settings_sex_female,
    settings_sex_male,
    settings_sex_menu,
)
from travel_agent.callbacks.start import start
from travel_agent.context import Context

if typing.TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine


async def post_init(application: Application) -> None:
    engine: AsyncEngine = application.bot_data["db_engine"]
    async with engine.begin() as connection:
        await connection.run_sync(orm_registry.metadata.create_all)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("telegram").setLevel(logging.DEBUG)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    application = (
        Application.builder()
        .token(os.getenv("TELEGRAM_TOKEN"))
        .post_init(post_init)
        .context_types(ContextTypes(Context))
        .defaults(Defaults(parse_mode=ParseMode.HTML))
        .build()
    )

    application.bot_data["db_engine"] = create_async_engine(os.getenv("DB_URL"))
    application.bot_data["db_session_factory"] = async_sessionmaker(
        application.bot_data["db_engine"]
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))

    application.add_handler(CommandHandler("settings", settings_menu))
    application.add_handler(CallbackQueryHandler(settings_sex_menu, "^settings_sex$"))
    application.add_handler(
        CallbackQueryHandler(settings_sex_male, "^settings_sex_male$")
    )
    application.add_handler(
        CallbackQueryHandler(settings_sex_female, "^settings_sex_female$")
    )
    application.add_handler(
        CallbackQueryHandler(back_to_settings_menu, "^settings_sex_back$")
    )

    application.add_handler(
        ConversationHandler(
            entry_points=[CallbackQueryHandler(settings_age, "^settings_age$")],
            states={1: [MessageHandler(filters.TEXT, settings_age_answered)]},
            fallbacks=[],
        )
    )

    application.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("newtravel", travel.entry_point)],
            states={1: [MessageHandler(filters.TEXT, travel.name)]},
            fallbacks=[],
        )
    )
    application.add_handler(
        ConversationHandler(
            entry_points=[CallbackQueryHandler(travel.add_bio, "travel_bio")],
            states={1: [MessageHandler(filters.TEXT, travel.bio)]},
            fallbacks=[],
        )
    )

    application.run_polling()


if __name__ == "__main__":
    main()
