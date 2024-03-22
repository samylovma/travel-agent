from telegram import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from telegram.ext import (
    BaseHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from travel_agent.context import Context
from travel_agent.middlewares import middlewares
from travel_agent.models import Note
from travel_agent.utils import callback_query, check_callback_data, message


def create_handlers() -> list[BaseHandler]:
    return [
        MessageHandler(filters.Document.ALL | filters.PHOTO, note_entry),
        CallbackQueryHandler(
            note_travel, lambda data: check_callback_data(data, "note_travel")
        ),
        CallbackQueryHandler(
            note_public, lambda data: check_callback_data(data, "note_public")
        ),
    ]


@middlewares
@message
async def note_entry(message: Message, context: Context) -> int:
    note_id: str
    if message.photo:
        note_id = message.photo[0].file_id
    if message.document:
        note_id = message.document.file_id

    user = await context.user_repo.get(message.from_user.id)
    await message.reply_text(
        "Сохранил! Укажи к какому путешествию прикрепить её, "
        "чтобы тебе было её легче найти. :)",
        reply_markup=InlineKeyboardMarkup.from_column(
            [
                InlineKeyboardButton(
                    f"«{travel.name}»",
                    callback_data=("note_travel", note_id, travel.id),
                )
                for travel in user.travels
            ]
        ),
    )


@middlewares
@callback_query
async def note_travel(callback_query: CallbackQuery, context: Context) -> int:
    note_id: str = callback_query.data[1]
    travel_id: int = callback_query.data[2]
    note = Note(
        id=note_id,
        user_id=callback_query.from_user.id,
        travel_id=travel_id,
        is_private=True,
    )
    await context.note_repo.add(note)
    await callback_query.answer()
    await callback_query.message.reply_text(
        "Добавил! "
        "Если хочешь, чтобы заметка была доступна всем в путешествии, "
        "то нажми на кнопку.",
        reply_markup=InlineKeyboardMarkup.from_button(
            InlineKeyboardButton(
                "Сделать заметку публичной", callback_data=("note_public", note.id)
            )
        ),
    )


@middlewares
@callback_query
async def note_public(callback_query: CallbackQuery, context: Context) -> int:
    note_id: int = callback_query.data[1]
    note = await context.note_repo.get(note_id)
    note.is_private = False
    await context.note_repo.update(note)
    await callback_query.answer("Сделано!")
