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


async def travel_menu(message: Message, context: Context, travel: Travel) -> None:
    me = await context.bot.get_me()
    invite_token: str = await context.invite_token_repo.create(travel.id)
    await message.reply_text(
        f"<b>Путешествие «{travel.name}»</b>\n"
        f"<b>Описание:</b> «{travel.bio}».\n\n"
        "Кнопка «Пригласить друга» предложит тебе отправить "
        "ссылку-приглашение путникам, с которыми ты хочешь отправиться в путешествие. "
        "Ссылка действует ~ 24 часа с момента отправки этого сообщения.",
        reply_markup=InlineKeyboardMarkup.from_column(
            (
                InlineKeyboardButton(
                    "Изменить описание", callback_data=("travel_bio", travel.id)
                ),
                InlineKeyboardButton(
                    "Список заметок", callback_data=("travel_note_list", travel.id)
                ),
                InlineKeyboardButton(
                    "Список локаций", callback_data=("travel_location_list", travel.id)
                ),
                InlineKeyboardButton(
                    "Пригласить друга",
                    url=(
                        "tg://msg_url?url="
                        + create_deep_linked_url(me.username, invite_token)
                    ),
                ),
            )
        ),
    )


@middlewares
@message_callback
async def travels_cmd(message: Message, context: Context) -> None:
    user = await context.user_repo.get(message.from_user.id)
    await message.reply_text(
        "<b>Список твоих путешествий:</b>",
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
    await callback_query.message.edit_text("Список твоих путешествий:")
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
    await callback_query.message.edit_text(
        f"<b>Путешествие «{travel.name}»</b>\n"
        f"<b>Описание:</b> «{travel.bio}».\n\n"
        "Кнопка «Пригласить друга» предложит тебе отправить "
        "ссылку-приглашение путникам, с которыми ты хочешь отправиться в путешествие. "
        "Ссылка действует ~ 24 часа с момента отправки этого сообщения.",
    )
    await callback_query.message.edit_reply_markup(
        InlineKeyboardMarkup.from_column(
            (
                InlineKeyboardButton(
                    "Изменить описание", callback_data=("travel_bio", travel.id)
                ),
                InlineKeyboardButton(
                    "Список заметок", callback_data=("travel_note_list", travel.id)
                ),
                InlineKeyboardButton(
                    "Список локаций", callback_data=("travel_location_list", travel.id)
                ),
                InlineKeyboardButton(
                    "Пригласить друга",
                    url=(
                        "tg://msg_url?url="
                        + create_deep_linked_url(me.username, invite_token)
                    ),
                ),
                InlineKeyboardButton("<< Все путешествия", callback_data="travels"),
            )
        )
    )


@middlewares
@message_callback
async def newtravel_entry(message: Message, _: Context) -> int:
    await message.reply_text(
        "Придумайте название для путешествия, постарайтесь сделать его уникальным!\n"
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
    await callback_query.message.reply_text("Напишите описание для путешествия.")
    return ChangeBioState.BIO.value


@middlewares
@message_callback
async def change_bio_end(message: Message, context: Context) -> int:
    travel_id: int = context.user_data["travel_id"]
    await context.travel_repo.update(
        Travel(id=travel_id, bio=message.text), attribute_names=("bio",)
    )
    travel = await context.travel_repo.get(travel_id)
    await travel_menu(message, context, travel)
    return ChangeBioState.END.value
