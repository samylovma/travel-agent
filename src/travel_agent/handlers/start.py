import telegram

from travel_agent.context import Context
from travel_agent.middlewares import middlewares
from travel_agent.utils import get_mention, message_callback


@middlewares
@message_callback
async def start(message: telegram.Message, context: Context) -> None:
    if context.args:
        invite_token: str = context.args[0]
        travel_id = await context.invite_token_repo.get_travel_id(invite_token)
        if travel_id is None:
            return

        await context.travel_repo.add_user_to(
            travel_id=travel_id, user_id=message.from_user.id
        )
        travel = await context.travel_repo.get(travel_id)
        for user in travel.users:
            if user.id == message.from_user.id:
                await message.reply_text(
                    "Тебя пригласили в путешествие «{travel.name}»!"
                )
                continue
            await context.bot.send_message(
                chat_id=user.id,
                text=(
                    f"Добавлен Путник в путешествие «{travel.name}»: "
                    + get_mention(message.from_user)
                    + "."
                ),
            )
        return

    await message.reply_text(
        "Здравствуй, Путник!\n"
        "Я — Тревел Агент. Cтрашно звучит, не правда ли? Сейчас всё расскажу!\n"
        "Я могу взять на себя твои рутинные дела во время путешествия.\n"
        "Если хочешь рассказать о себе больше, жми /settings.\n"
        "/help — список команд.\n"
    )
