from datetime import UTC, date, datetime
from typing import TYPE_CHECKING, cast

from telegram import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from telegram.ext import (
    BaseHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from travel_agent.context import Context
from travel_agent.handlers.travel import travel_menu
from travel_agent.middlewares import middlewares
from travel_agent.models import Location
from travel_agent.utils import (
    callback_query_callback,
    check_callback_data,
    message_callback,
)

if TYPE_CHECKING:
    from travel_agent.repositories import Place


def create_handlers() -> list[BaseHandler]:
    return [
        ConversationHandler(
            entry_points=[
                CallbackQueryHandler(
                    add_location_entry,
                    lambda data: check_callback_data(data, "newlocation"),
                )
            ],
            states={
                1: [MessageHandler(filters.TEXT, add_location_coord)],
                2: [CallbackQueryHandler(add_location_start_at)],
                3: [MessageHandler(filters.TEXT, add_location_end_at)],
                4: [MessageHandler(filters.TEXT, add_location_end)],
            },
            fallbacks=[],
        ),
    ]


@middlewares
@callback_query_callback
async def add_location_entry(callback_query: CallbackQuery, context: Context) -> int:
    travel_id = cast(int, callback_query.data[1])  # type: ignore[index]
    context.user_data["travel_id"] = travel_id  # type: ignore[index]
    await callback_query.answer()
    await callback_query.message.reply_text("Напишите адрес или отправьте геолокацию.")
    return 1


@middlewares
@message_callback
async def add_location_coord(message: Message, context: Context) -> int:
    places: list[Place] = await context.map_search_repo.search(message.text)
    await message.reply_text(
        "Что ты имел в виду? :)",
        reply_markup=InlineKeyboardMarkup.from_column(
            [
                InlineKeyboardButton(f"{place.address}", callback_data=place)
                for place in places
            ]
        ),
    )
    return 2


@middlewares
@callback_query_callback
async def add_location_start_at(
    callback_query: CallbackQuery, context: Context
) -> None:
    context.user_data["place"] = callback_query.data
    await callback_query.edit_message_text(
        "Отличное место! "
        "С какой даты вы планируете там быть? Отправьте в формате ДД.ММ.ГГГГ."
    )
    return 3


@middlewares
@message_callback
async def add_location_end_at(message: Message, context: Context) -> None:
    dt = datetime.strptime(message.text, "%d.%m.%Y").replace(tzinfo=UTC)
    context.user_data["start_at"] = dt.date()
    await message.reply_text(
        "А до какого числа там задержитесь? Отправьте в формате ДД.ММ.ГГГГ."
    )
    return 4


@middlewares
@message_callback
async def add_location_end(message: Message, context: Context) -> int:
    travel_id: int = context.user_data["travel_id"]
    place: Place = context.user_data["place"]
    start_at: date = context.user_data["start_at"]

    dt = datetime.strptime(message.text, "%d.%m.%Y").replace(tzinfo=UTC)
    end_at: date = dt.date()

    if end_at < start_at:
        await message.reply_text(
            "Проверьте, дата конца пребывания должна быть позже даты начала."
        )
        return 4

    await context.location_repo.add(
        Location(
            travel_id=travel_id,
            name=place.name,
            lat=place.lat,
            lon=place.lon,
            start_at=start_at,
            end_at=end_at,
        )
    )

    travel = await context.travel_repo.get(travel_id)
    await travel_menu(message, context, travel)

    return ConversationHandler.END
