import logging
import os
import typing

from advanced_alchemy.base import orm_registry
from redis.asyncio import ConnectionPool
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

from travel_agent.context import Context
from travel_agent.handlers import travel
from travel_agent.handlers.help import help
from travel_agent.handlers.settings import (
    back_to_settings,
    settings,
    settings_age,
    settings_age_answered,
    settings_sex,
    settings_sex_female,
    settings_sex_male,
)
from travel_agent.handlers.start import start

if typing.TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine


async def post_init(application: Application) -> None:
    engine: AsyncEngine = application.bot_data["db_engine"]
    async with engine.begin() as connection:
        await connection.run_sync(orm_registry.metadata.create_all)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
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

    application.bot_data["redis_pool"] = ConnectionPool.from_url(os.getenv("REDIS_URL"))

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))

    application.add_handler(CommandHandler("settings", settings))
    application.add_handler(CallbackQueryHandler(settings_sex, "^settings_sex$"))
    application.add_handler(
        CallbackQueryHandler(settings_sex_male, "^settings_sex_male$")
    )
    application.add_handler(
        CallbackQueryHandler(settings_sex_female, "^settings_sex_female$")
    )
    application.add_handler(
        CallbackQueryHandler(back_to_settings, "^settings_sex_back$")
    )

    application.add_handler(
        ConversationHandler(
            entry_points=[CallbackQueryHandler(settings_age, "^settings_age$")],
            states={1: [MessageHandler(filters.TEXT, settings_age_answered)]},
            fallbacks=[],
        )
    )

    application.add_handlers(travel.create_handlers())

    application.run_polling()


if __name__ == "__main__":
    main()
