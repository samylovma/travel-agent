from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

from travel_agent.context import Context
from travel_agent.middlewares import middlewares
from travel_agent.models import SexEnum


@middlewares
async def settings_menu(update: Update, _: Context) -> None:
    await update.message.reply_text(
        "Тут ты можешь больше рассказать о себе. :)",
        reply_markup=InlineKeyboardMarkup.from_column(
            (
                InlineKeyboardButton("Указать возраст", callback_data="settings_age"),
                InlineKeyboardButton("Добавить пол", callback_data="settings_sex"),
            )
        ),
    )


@middlewares
async def back_to_settings_menu(update: Update, _: Context) -> None:
    await update.effective_message.edit_text(
        "Тут ты можешь больше рассказать о себе. :)",
    )
    await update.effective_message.edit_reply_markup(
        InlineKeyboardMarkup.from_column(
            (
                InlineKeyboardButton("Указать возраст", callback_data="settings_age"),
                InlineKeyboardButton("Добавить пол", callback_data="settings_sex"),
            )
        )
    )


@middlewares
async def settings_age(update: Update, _: Context) -> int:
    await update.callback_query.answer()
    await update.effective_message.reply_text(
        "В ответ на это сообщение напиши свой возраст"
    )
    return 1


@middlewares
async def settings_age_answered(update: Update, context: Context) -> int:
    try:
        age = int(update.effective_message.text)
    except ValueError:
        await update.effective_message.reply_text("Неверный формат")
    user = context.data["user"]
    user.age = age
    await context.user_repo.update(user)
    await update.effective_message.reply_text("Отлично!")
    await settings_menu(update, context)
    return -1


@middlewares
async def settings_sex_menu(update: Update, _: Context) -> None:
    await update.effective_message.edit_text("Выберите пол:")
    await update.effective_message.edit_reply_markup(
        InlineKeyboardMarkup.from_column(
            (
                InlineKeyboardButton("Мужской", callback_data="settings_sex_male"),
                InlineKeyboardButton("Женский", callback_data="settings_sex_female"),
                InlineKeyboardButton("Назад", callback_data="settings_sex_back"),
            )
        )
    )


@middlewares
async def settings_sex_male(update: Update, context: Context) -> None:
    user = context.data["user"]
    user.sex = SexEnum.male
    await context.user_repo.update(user)
    await back_to_settings_menu(update, context)


@middlewares
async def settings_sex_female(update: Update, context: Context) -> None:
    user = context.data["user"]
    user.sex = SexEnum.female
    await context.user_repo.update(user)
    await back_to_settings_menu(update, context)
