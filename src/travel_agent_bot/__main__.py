import logging
from os import getenv

from telegram.ext import Application, MessageHandler, filters

from .callbacks.echo import echo


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    application = Application.builder().token(getenv("TELEGRAM_TOKEN")).build()
    application.add_handler(MessageHandler(filters.TEXT, echo))
    application.run_polling()


if __name__ == "__main__":
    main()
