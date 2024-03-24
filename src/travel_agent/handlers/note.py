from dataclasses import dataclass

from telegram import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from telegram.error import BadRequest
from telegram.ext import (
    BaseHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from travel_agent.context import Context
from travel_agent.middlewares import middlewares
from travel_agent.models import Note
from travel_agent.utils import (
    callback_query_callback,
    check_callback_data,
    message_callback,
)


def create_handlers() -> list[BaseHandler]:
    return [
        CallbackQueryHandler(
            note_list, lambda data: check_callback_data(data, "travel_note_list")
        ),
        CallbackQueryHandler(
            show_note, lambda data: check_callback_data(data, "travel_note")
        ),
        MessageHandler(filters.Document.ALL | filters.PHOTO, note_entry),
        CallbackQueryHandler(
            note_travel, lambda data: check_callback_data(data, "note_travel")
        ),
        CallbackQueryHandler(
            note_public, lambda data: check_callback_data(data, "note_public")
        ),
    ]


@dataclass
class TempNote:
    id: str
    name: str
    travel_id: int


@middlewares
@callback_query_callback
async def note_list(callback_query: CallbackQuery, context: Context) -> None:
    travel_id: int = callback_query.data[1]
    travel = await context.travel_repo.get(travel_id)
    await callback_query.message.edit_text(
        f"<b>Заметки путешествия «{travel.name}»</b>"
    )
    await callback_query.message.edit_reply_markup(
        InlineKeyboardMarkup.from_column(
            [
                *[
                    InlineKeyboardButton(
                        f"«{note.name}»", callback_data=("travel_note", note.id)
                    )
                    for note in travel.notes
                    if (
                        note.is_private is False
                        or note.user_id == callback_query.from_user.id
                    )
                ],
                InlineKeyboardButton(
                    "<< К путешествию", callback_data=("travel", travel_id)
                ),
            ]
        )
    )


@middlewares
@callback_query_callback
async def show_note(callback_query: CallbackQuery, context: Context) -> None:
    note_id: int = callback_query.data[1]
    note = await context.note_repo.get(note_id)
    await callback_query.answer()
    try:
        await callback_query.message.reply_photo(note.id, caption=note.name)
    except BadRequest:
        await callback_query.message.reply_document(note.id, caption=note.name)


@middlewares
@message_callback
async def note_entry(message: Message, context: Context) -> int:
    note_id: str
    if message.photo:
        note_id = message.photo[0].file_id
    if message.document:
        note_id = message.document.file_id

    user = await context.user_repo.get(message.from_user.id)
    await message.reply_text(
        "Увидел! Укажи к какому путешествию её прикрепить.",
        reply_markup=InlineKeyboardMarkup.from_column(
            [
                InlineKeyboardButton(
                    f"«{travel.name}»",
                    callback_data=(
                        "note_travel",
                        TempNote(id=note_id, name=message.caption, travel_id=travel.id),
                    ),
                )
                for travel in user.travels
            ]
        ),
    )

    return 1


@middlewares
@callback_query_callback
async def note_travel(callback_query: CallbackQuery, context: Context) -> None:
    temp_note: TempNote = callback_query.data[1]

    note = Note(
        id=temp_note.id,
        name=temp_note.name,
        user_id=callback_query.from_user.id,
        travel_id=temp_note.travel_id,
        is_private=True,
    )
    await context.note_repo.add(note)

    travel = await context.travel_repo.get(temp_note.travel_id)
    await callback_query.message.edit_text(
        f"Добавил в путешествие «{travel.name}»!\n"
        "Если хочешь, чтобы заметка была доступна всем в путешествии, "
        "то нажми на кнопку.",
    )

    await callback_query.message.edit_reply_markup(
        InlineKeyboardMarkup.from_button(
            InlineKeyboardButton(
                "Сделать заметку публичной", callback_data=("note_public", note.id)
            )
        ),
    )


@middlewares
@callback_query_callback
async def note_public(callback_query: CallbackQuery, context: Context) -> None:
    note_id: int = callback_query.data[1]
    note = await context.note_repo.get(note_id)
    note.is_private = False
    await context.note_repo.update(note)

    await callback_query.answer("Сделано!")
    await callback_query.message.delete()
