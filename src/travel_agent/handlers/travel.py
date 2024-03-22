import enum

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
from travel_agent.utils import callback_query, message


class NewTravelState(enum.Enum):
    NAME = 0
    END = ConversationHandler.END


class ChangeBioState(enum.Enum):
    BIO = 0
    END = ConversationHandler.END


def create_handlers() -> list[BaseHandler]:
    return [
        CommandHandler("travels", travels),
        ConversationHandler(
            entry_points=[CommandHandler("newtravel", newtravel_entry)],
            states={
                NewTravelState.NAME: [MessageHandler(filters.TEXT, newtravel_name)]
            },
            fallbacks=[],
        ),
        ConversationHandler(
            entry_points=[
                CallbackQueryHandler(
                    change_bio_entry, lambda data: data[0] == "travel_bio"
                )
            ],
            states={ChangeBioState.BIO: [MessageHandler(filters.TEXT, change_bio_end)]},
            fallbacks=[],
        ),
    ]


async def travel_menu(message: Message, context: Context, travel: Travel) -> None:
    me = await context.bot.get_me()
    invite_token: str = await context.invite_token_repo.create(travel.id)
    await message.reply_text(
        f"<b>Путешествие «{travel.name}» № {travel.id}</b>\n"
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
@message
async def travels(message: Message, context: Context) -> None:
    user = await context.user_repo.get(message.from_user.id)
    buttons = [
        InlineKeyboardButton(
            f"«{travel.name}» № {travel.id}", callback_data=("travel", travel.id)
        )
        for travel in user.travels
    ]
    markup = InlineKeyboardMarkup.from_column(buttons)
    await message.reply_text("Список твоих путешествий:", reply_markup=markup)


@middlewares
@callback_query
async def travel(callback_query: CallbackQuery, context: Context) -> None:
    pass


@middlewares
@message
async def newtravel_entry(message: Message, _: Context) -> NewTravelState:
    await message.reply_text(
        "Придумайте название для путешествия, постарайтесь сделать его уникальным!\n"
        "<blockquote>Как корабль назовёшь, так он и поплывёт.</blockquote>"
    )
    return NewTravelState.NAME


@middlewares
@message
async def newtravel_name(message: Message, context: Context) -> NewTravelState:
    try:
        travel = await context.travel_repo.add(Travel(name=message.text))
    except IntegrityError:
        await message.reply_text(
            "К сожалению, это название уже занято. Попробуйте другое."
        )
        return NewTravelState.NAME

    travel_id = travel.id

    user = await context.user_repo.get(message.from_user.id)
    await context.travel_repo.add_user_to(travel_id=travel.id, user_id=user.id)

    travel = await context.travel_repo.get(travel_id)
    await travel_menu(message, context, travel)

    return NewTravelState.END


@middlewares
@callback_query
async def change_bio_entry(
    callback_query: CallbackQuery, context: Context
) -> ChangeBioState:
    context.user_data["travel_id"] = callback_query.data[1]
    await callback_query.answer()
    await callback_query.message.reply_text("Напишите описание для путешествия.")
    return ChangeBioState.BIO


@middlewares
@message
async def change_bio_end(message: Message, context: Context) -> ChangeBioState:
    travel_id: int = context.user_data["travel_id"]
    await context.travel_repo.update(
        Travel(id=travel_id, bio=message.text), attribute_names=("bio",)
    )
    travel = await context.travel_repo.get(travel_id)
    await travel_menu(message, context, travel)
    return ChangeBioState.END
