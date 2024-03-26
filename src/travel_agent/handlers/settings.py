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

from travel_agent.context import Context
from travel_agent.middlewares import middlewares
from travel_agent.models import SexEnum, User
from travel_agent.utils import callback_query_callback, message_callback


def create_handlers() -> list[BaseHandler]:
    return [
        CommandHandler("settings", settings),
        ConversationHandler(
            entry_points=[CallbackQueryHandler(settings_age, "^settings_age$")],
            states={1: [MessageHandler(filters.TEXT, settings_age_answered)]},
            fallbacks=[],
        ),
        CallbackQueryHandler(settings_sex, "^settings_sex$"),
        CallbackQueryHandler(settings_sex_male, "^settings_sex_male$"),
        CallbackQueryHandler(settings_sex_female, "^settings_sex_female$"),
        CallbackQueryHandler(back_to_settings, "^settings_sex_back$"),
        ConversationHandler(
            entry_points=[CallbackQueryHandler(settings_city, "^settings_city$")],
            states={1: [MessageHandler(filters.TEXT, settings_city_answered)]},
            fallbacks=[],
        ),
        ConversationHandler(
            entry_points=[CallbackQueryHandler(settings_country, "^settings_country$")],
            states={1: [MessageHandler(filters.TEXT, settings_country_answered)]},
            fallbacks=[],
        ),
        ConversationHandler(
            entry_points=[CallbackQueryHandler(settings_bio, "^settings_bio$")],
            states={1: [MessageHandler(filters.TEXT, settings_bio_answered)]},
            fallbacks=[],
        ),
    ]


def get_text(user: User) -> str:
    sex_to_str = {
        "male": "Мужской",
        "female": "Женский",
        None: "",
    }
    return (
        "<b>Профиль</b>\n\n"
        f"<b>Возраст:</b> {user.age if user.age else ''}.\n"
        f"<b>Пол:</b> {sex_to_str[user.sex]}.\n"
        f"<b>Город:</b> {user.city if user.city else ''}.\n"
        f"<b>Страна:</b> {user.country if user.country else ''}.\n"
        f"<b>Описание:</b> «{user.bio if user.bio else ''}.»"
    )


async def settings_menu(message: Message, context: Context) -> None:
    user = await context.user_repo.get(message.from_user.id)
    await message.reply_text(
        get_text(user),
        reply_markup=InlineKeyboardMarkup.from_column(
            (
                InlineKeyboardButton("Указать возраст", callback_data="settings_age"),
                InlineKeyboardButton("Указать пол", callback_data="settings_sex"),
                InlineKeyboardButton("Указать город", callback_data="settings_city"),
                InlineKeyboardButton(
                    "Указать страну", callback_data="settings_country"
                ),
                InlineKeyboardButton("Изменить описание", callback_data="settings_bio"),
            )
        ),
    )


async def back_to_settings_menu(
    callback_query: CallbackQuery, context: Context
) -> None:
    user = await context.user_repo.get(callback_query.from_user.id)
    await callback_query.edit_message_text(get_text(user))
    await callback_query.edit_message_reply_markup(
        InlineKeyboardMarkup.from_column(
            (
                InlineKeyboardButton("Указать возраст", callback_data="settings_age"),
                InlineKeyboardButton("Указать пол", callback_data="settings_sex"),
                InlineKeyboardButton("Указать город", callback_data="settings_city"),
                InlineKeyboardButton(
                    "Указать страну", callback_data="settings_country"
                ),
                InlineKeyboardButton("Изменить описание", callback_data="settings_bio"),
            )
        )
    )


@middlewares
@message_callback
async def settings(message: Message, context: Context) -> None:
    await settings_menu(message, context)


@middlewares
@callback_query_callback
async def back_to_settings(callback_query: CallbackQuery, context: Context) -> None:
    await back_to_settings_menu(callback_query, context)


@middlewares
@callback_query_callback
async def settings_age(callback_query: CallbackQuery, _: Context) -> int:
    await callback_query.answer()
    await callback_query.message.reply_text(
        "В ответ на это сообщение напиши свой возраст."
    )
    return 1


@middlewares
@message_callback
async def settings_age_answered(message: Message, context: Context) -> int:
    try:
        age = int(message.text)
    except ValueError:
        await message.reply_text("Неверный формат")
    user = await context.user_repo.get(message.from_user.id)
    user.age = age
    await context.user_repo.update(user)
    await settings_menu(message, context)
    return ConversationHandler.END


@middlewares
@callback_query_callback
async def settings_sex(callback_query: CallbackQuery, _: Context) -> None:
    await callback_query.message.edit_text("Выберите пол:")
    await callback_query.message.edit_reply_markup(
        InlineKeyboardMarkup.from_column(
            (
                InlineKeyboardButton("Мужской", callback_data="settings_sex_male"),
                InlineKeyboardButton("Женский", callback_data="settings_sex_female"),
                InlineKeyboardButton("Назад", callback_data="settings_sex_back"),
            )
        )
    )


@middlewares
@callback_query_callback
async def settings_sex_male(callback_query: CallbackQuery, context: Context) -> None:
    user = await context.user_repo.get(callback_query.from_user.id)
    user.sex = SexEnum.male
    await context.user_repo.update(user)
    await callback_query.answer("Обновлено!")
    await back_to_settings_menu(callback_query, context)


@middlewares
@callback_query_callback
async def settings_sex_female(callback_query: CallbackQuery, context: Context) -> None:
    user = await context.user_repo.get(callback_query.from_user.id)
    user.sex = SexEnum.female
    await context.user_repo.update(user)
    await callback_query.answer("Обновлено!")
    await back_to_settings_menu(callback_query, context)


@middlewares
@callback_query_callback
async def settings_city(callback_query: CallbackQuery, _: Context) -> int:
    await callback_query.answer()
    await callback_query.message.reply_text(
        "В ответ на это сообщение напиши свой город проживания."
    )
    return 1


@middlewares
@message_callback
async def settings_city_answered(message: Message, context: Context) -> int:
    user = await context.user_repo.get(message.from_user.id)
    user.city = message.text
    await context.user_repo.update(user)
    await settings_menu(message, context)
    return ConversationHandler.END


@middlewares
@callback_query_callback
async def settings_country(callback_query: CallbackQuery, _: Context) -> int:
    await callback_query.answer()
    await callback_query.message.reply_text(
        "В ответ на это сообщение напиши свою страну проживания."
    )
    return 1


@middlewares
@message_callback
async def settings_country_answered(message: Message, context: Context) -> int:
    user = await context.user_repo.get(message.from_user.id)
    user.country = message.text
    await context.user_repo.update(user)
    await settings_menu(message, context)
    return ConversationHandler.END


@middlewares
@callback_query_callback
async def settings_bio(callback_query: CallbackQuery, _: Context) -> int:
    await callback_query.answer()
    await callback_query.message.reply_text(
        "В ответ на это сообщение напиши пару слов о себе."
    )
    return 1


@middlewares
@message_callback
async def settings_bio_answered(message: Message, context: Context) -> int:
    user = await context.user_repo.get(message.from_user.id)
    user.bio = message.text
    await context.user_repo.update(user)
    await settings_menu(message, context)
    return ConversationHandler.END
