from telegram import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from travel_agent.context import Context
from travel_agent.middlewares import middlewares
from travel_agent.models import SexEnum
from travel_agent.utils import callback_query, message


async def settings_menu(message: Message, _: Context) -> None:
    await message.reply_text(
        "Тут ты можешь больше рассказать о себе. :)",
        reply_markup=InlineKeyboardMarkup.from_column(
            (
                InlineKeyboardButton("Указать возраст", callback_data="settings_age"),
                InlineKeyboardButton("Добавить пол", callback_data="settings_sex"),
            )
        ),
    )


async def back_to_settings_menu(message: Message, _: Context) -> None:
    await message.edit_text(
        "Тут ты можешь больше рассказать о себе. :)",
    )
    await message.edit_reply_markup(
        InlineKeyboardMarkup.from_column(
            (
                InlineKeyboardButton("Указать возраст", callback_data="settings_age"),
                InlineKeyboardButton("Добавить пол", callback_data="settings_sex"),
            )
        )
    )


@middlewares
@message
async def settings(message: Message, _: Context) -> None:
    await message.reply_text(
        "Тут ты можешь больше рассказать о себе. :)",
        reply_markup=InlineKeyboardMarkup.from_column(
            (
                InlineKeyboardButton("Указать возраст", callback_data="settings_age"),
                InlineKeyboardButton("Добавить пол", callback_data="settings_sex"),
            )
        ),
    )


@middlewares
@callback_query
async def back_to_settings(callback_query: CallbackQuery, context: Context) -> None:
    await back_to_settings_menu(callback_query.message, context)


@middlewares
@callback_query
async def settings_age(callback_query: CallbackQuery, _: Context) -> int:
    await callback_query.answer()
    await callback_query.message.reply_text(
        "В ответ на это сообщение напиши свой возраст."
    )
    return 1


@middlewares
@message
async def settings_age_answered(message: Message, context: Context) -> int:
    try:
        age = int(message.text)
    except ValueError:
        await message.reply_text("Неверный формат")
    user = await context.user_repo.get(message.from_user.id)
    user.age = age
    await context.user_repo.update(user)
    await message.reply_text("Отлично!")
    await settings_menu(message, context)
    return -1


@middlewares
@callback_query
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
@callback_query
async def settings_sex_male(callback_query: CallbackQuery, context: Context) -> None:
    user = await context.user_repo.get(callback_query.from_user.id)
    user.sex = SexEnum.male
    await context.user_repo.update(user)
    await back_to_settings_menu(callback_query.message, context)


@middlewares
@callback_query
async def settings_sex_female(callback_query: CallbackQuery, context: Context) -> None:
    user = await context.user_repo.get(callback_query.from_user.id)
    user.sex = SexEnum.female
    await context.user_repo.update(user)
    await back_to_settings_menu(callback_query.message, context)
