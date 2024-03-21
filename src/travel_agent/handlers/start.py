from telegram import Message
from telegram.helpers import mention_html

from travel_agent.context import Context
from travel_agent.middlewares import middlewares
from travel_agent.utils import message


@middlewares
@message
async def start(message: Message, context: Context) -> None:
    if context.args:
        invite_token: str = context.args[0]
        travel_id = await context.invite_token_repo.get_travel_id(invite_token)
        if isinstance(travel_id, int):
            user = await context.user_repo.get(message.from_user.id)
            await context.travel_repo.add_user_to(travel_id=travel_id, user_id=user.id)
            travel = await context.travel_repo.get(id=travel_id)
            for user in travel.users:
                await context.bot.send_message(
                    chat_id=user.id,
                    text=(
                        "Добавлен новый Путник в путешествие: "
                        + mention_html(message.from_user.id, message.from_user.name)
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
