import logging
from os import getenv

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from telegram.ext import Application, MessageHandler, filters

from .callbacks.echo import echo
from .models import Base


async def post_init(application: Application) -> None:
    engine: AsyncEngine = application.bot_data["db_engine"]
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    application = (
        Application.builder()
        .token(getenv("TELEGRAM_TOKEN"))
        .post_init(post_init)
        .build()
    )
    application.bot_data["db_engine"] = create_async_engine(getenv("DB_URL"))
    application.add_handler(MessageHandler(filters.TEXT, echo))
    application.run_polling()


if __name__ == "__main__":
    main()
