import logging
import os
import typing

from advanced_alchemy.base import orm_registry
from fluent_compiler.bundle import FluentBundle
from redis.asyncio import ConnectionPool
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from telegram import BotCommand
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    Defaults,
)

from travel_agent import handlers
from travel_agent.constants import LOCALES_DIR
from travel_agent.context import Context
from travel_agent.handlers.start import start
from travel_agent.l10n import Localization

if typing.TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine


async def post_init(application: Application) -> None:
    engine: AsyncEngine = application.bot_data["db_engine"]
    async with engine.begin() as connection:
        await connection.run_sync(orm_registry.metadata.create_all)

    await application.bot.set_my_commands(
        (
            BotCommand("/start", "Запустить бота"),
            BotCommand("/settings", "Настройки профиля"),
            BotCommand("/help", "Список команд"),
            BotCommand("/travels", "Меню путешествий"),
            BotCommand("/newtravel", "Создать новое путешествие"),
        )
    )


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    application = (
        Application.builder()
        .token(os.getenv("TELEGRAM_TOKEN"))
        .post_init(post_init)
        .context_types(ContextTypes(Context))
        .defaults(Defaults(parse_mode=ParseMode.HTML))
        .arbitrary_callback_data(True)  # noqa: FBT003
        .build()
    )

    application.bot_data["db_engine"] = create_async_engine(os.getenv("DB_URL"))
    application.bot_data["db_session_factory"] = async_sessionmaker(
        application.bot_data["db_engine"]
    )

    application.bot_data["redis_pool"] = ConnectionPool.from_url(os.getenv("REDIS_URL"))

    application.bot_data["l10n"] = Localization(
        FluentBundle.from_files("ru", [LOCALES_DIR / "ru.ftl"])
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handlers(handlers.help.create_handlers())
    application.add_handlers(handlers.settings.create_handlers())
    application.add_handlers(handlers.travel.create_handlers())
    application.add_handlers(handlers.note.create_handlers())
    application.add_handlers(handlers.locations.create_handlers())
    application.add_handlers(handlers.routes.create_handlers())

    application.run_polling()


if __name__ == "__main__":
    main()
