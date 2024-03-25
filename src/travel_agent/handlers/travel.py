import enum
import typing

from sqlalchemy.exc import IntegrityError
from telegram import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from telegram.ext import (
    BaseHandler,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
from telegram.helpers import create_deep_linked_url

from travel_agent.context import Context
from travel_agent.middlewares import middlewares
from travel_agent.models import Travel
from travel_agent.utils import (
    callback_query_callback,
    check_callback_data,
    message_callback,
)


class NewTravelState(enum.Enum):
    NAME = 0
    END = ConversationHandler.END


class ChangeBioState(enum.Enum):
    BIO = 0
    END = ConversationHandler.END


def create_handlers() -> list[BaseHandler]:
    return [
        CommandHandler("travels", travels_cmd),
        CallbackQueryHandler(
            travels_button, lambda data: check_callback_data(data, "travels")
        ),
        CallbackQueryHandler(travel, lambda data: check_callback_data(data, "travel")),
        ConversationHandler(
            entry_points=[CommandHandler("newtravel", newtravel_entry)],
            states={
                NewTravelState.NAME.value: [
                    MessageHandler(filters.TEXT, newtravel_name)
                ]
            },
            fallbacks=[],
        ),
        ConversationHandler(
            entry_points=[
                CallbackQueryHandler(
                    change_bio_entry,
                    lambda data: check_callback_data(data, "travel_bio"),
                )
            ],
            states={
                ChangeBioState.BIO.value: [MessageHandler(filters.TEXT, change_bio_end)]
            },
            fallbacks=[],
        ),
    ]


def build_keyboard(travel_id: int, bot_username: str, invite_token: str) -> None:
    return InlineKeyboardMarkup.from_column(
        (
            InlineKeyboardButton(
                "📝 Изменить описание", callback_data=("travel_bio", travel_id)
            ),
            InlineKeyboardButton(
                "🗒️ Заметки", callback_data=("travel_note_list", travel_id)
            ),
            InlineKeyboardButton("📍 Локации", callback_data=("locations", travel_id)),
            InlineKeyboardButton(
                "🗺️ Маршрут",
                callback_data=("travel_build_full_route", travel_id),
            ),
            InlineKeyboardButton(
                "🔗 Пригласить",
                url=(
                    "tg://msg_url?url="
                    + create_deep_linked_url(bot_username, invite_token)
                ),
            ),
            InlineKeyboardButton("<< Все путешествия", callback_data="travels"),
        )
    )


async def travel_menu(message: Message, context: Context, travel: Travel) -> None:
    me = await context.bot.get_me()
    invite_token: str = await context.invite_token_repo.create(travel.id)
    bio = travel.bio if travel.bio is not None else ""
    await message.reply_text(
        f"<b>🧳 «{travel.name}»</b>\n\n"
        f"<b>Описание:</b> «{bio}».\n\n"
        "Кнопка «Пригласить» предложит тебе "
        "<b>отправить ссылку-приглашение путникам</b>, "
        "с которыми ты хочешь отправиться в путешествие. "
        "Ссылка действует ~ 24 часа с момента отправки этого сообщения.",
        reply_markup=build_keyboard(
            travel_id=travel.id, bot_username=me.username, invite_token=invite_token
        ),
    )


@middlewares
@message_callback
async def travels_cmd(message: Message, context: Context) -> None:
    user = await context.user_repo.get(message.from_user.id)
    await message.reply_text(
        "<b>Твои путешествия</b>",
        reply_markup=InlineKeyboardMarkup.from_column(
            [
                InlineKeyboardButton(
                    f"«{travel.name}»", callback_data=("travel", travel.id)
                )
                for travel in user.travels
            ]
        ),
    )


@middlewares
@callback_query_callback
async def travels_button(callback_query: CallbackQuery, context: Context) -> None:
    user = await context.user_repo.get(callback_query.from_user.id)
    await callback_query.message.edit_text("<b>Твои путешествия</b>")
    await callback_query.message.edit_reply_markup(
        InlineKeyboardMarkup.from_column(
            [
                InlineKeyboardButton(
                    f"«{travel.name}»", callback_data=("travel", travel.id)
                )
                for travel in user.travels
            ]
        )
    )


@middlewares
@callback_query_callback
async def travel(callback_query: CallbackQuery, context: Context) -> None:
    travel_id = typing.cast(int, callback_query.data[1])
    travel = await context.travel_repo.get(travel_id)
    me = await context.bot.get_me()
    invite_token: str = await context.invite_token_repo.create(travel.id)
    bio = travel.bio if travel.bio is not None else ""
    await callback_query.message.edit_text(
        f"<b>🧳 «{travel.name}»</b>\n\n"
        f"<b>Описание:</b> «{bio}».\n\n"
        "Кнопка «Пригласить» предложит тебе "
        "<b>отправить ссылку-приглашение путникам</b>, "
        "с которыми ты хочешь отправиться в путешествие. "
        "Ссылка действует ~ 24 часа с момента отправки этого сообщения.",
    )
    await callback_query.message.edit_reply_markup(
        build_keyboard(
            travel_id=travel.id, bot_username=me.username, invite_token=invite_token
        )
    )


@middlewares
@message_callback
async def newtravel_entry(message: Message, _: Context) -> int:
    await message.reply_text(
        "Придумай название для путешествия, постарайся сделать его уникальным!\n"
        "Как говорил капитан Врунгель,"
        "<blockquote>Как корабль назовёшь, так он и поплывёт.</blockquote>"
    )
    return NewTravelState.NAME.value


@middlewares
@message_callback
async def newtravel_name(message: Message, context: Context) -> int:
    try:
        travel = await context.travel_repo.add(Travel(name=message.text))
    except IntegrityError:
        await message.reply_text(
            "К сожалению, это название уже занято. Попробуйте другое."
        )
        return NewTravelState.NAME.value

    travel_id = travel.id

    user = await context.user_repo.get(message.from_user.id)
    await context.travel_repo.add_user_to(travel_id=travel.id, user_id=user.id)

    travel = await context.travel_repo.get(travel_id)
    await travel_menu(message, context, travel)

    return NewTravelState.END.value


@middlewares
@callback_query_callback
async def change_bio_entry(callback_query: CallbackQuery, context: Context) -> int:
    context.user_data["travel_id"] = typing.cast(int, callback_query.data[1])
    await callback_query.answer()
    await callback_query.message.reply_text("Придумай описание для путешествия.")
    return ChangeBioState.BIO.value


@middlewares
@message_callback
async def change_bio_end(message: Message, context: Context) -> int:
    travel_id: int = context.user_data["travel_id"]
    await context.travel_repo.update(
        Travel(id=travel_id, bio=message.text),
        attribute_names=("bio",),
    )
    travel = await context.travel_repo.get(travel_id)
    await travel_menu(message, context, travel)
    return ChangeBioState.END.value
