from typing import Literal

from sqlalchemy.exc import IntegrityError
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

from travel_agent.context import Context
from travel_agent.middlewares import middlewares
from travel_agent.models import Travel


@middlewares
async def entry_point(update: Update, _: Context) -> int:
    await update.effective_message.reply_text(
        "Придумайте название для путешествия, постарайтесь сделать его уникальным!\n"
        "<blockquote>Как корабль назовёшь, так он и поплывёт.</blockquote>"
    )
    return 1


@middlewares
async def name(update: Update, context: Context) -> int:
    try:
        travel = await context.travel_repo.add(
            Travel(name=update.effective_message.text)
        )
    except IntegrityError:
        await update.effective_message.reply_text(
            "К сожалению, это название уже занято. Попробуйте другое."
        )
        return 1
    await update.effective_message.reply_text(
        f"Отлично!\nИдентификатор: {travel.id}.\nИмя: {travel.name}.",
        reply_markup=InlineKeyboardMarkup.from_column(
            (
                InlineKeyboardButton(
                    "Добавить описание", callback_data=f"travel_bio_{travel.id}"
                ),
                InlineKeyboardButton(
                    "Добавить локацию", callback_data="travel_add_loc"
                ),
            )
        ),
    )
    return -1


@middlewares
async def add_bio(update: Update, context: Context) -> Literal[1]:
    context.user_data["travel_id"] = update.callback_query.data.split()[-1]
    await update.callback_query.answer()
    await update.effective_message.reply_text("Напишите описание для путешествия.")
    return 1


@middlewares
async def bio(update: Update, context: Context) -> Literal[-1]:
    travel_id = int(context.user_data["travel_id"].split("_")[-1])
    travel = await context.travel_repo.update_bio(travel_id, update.message.text)
    await update.effective_message.reply_text(
        f"Сделано!\nИдентификатор: {travel.id}.\nНазвание: {travel.name}.",
        reply_markup=InlineKeyboardMarkup.from_column(
            (
                InlineKeyboardButton(
                    "Изменить описание", callback_data=f"travel_bio_{travel.id}"
                ),
                InlineKeyboardButton(
                    "Добавить локацию", callback_data="travel_add_loc"
                ),
            )
        ),
    )
    return -1
