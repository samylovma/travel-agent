import io
from typing import cast

import staticmap
from telegram import CallbackQuery
from telegram.constants import ChatAction
from telegram.ext import BaseHandler, CallbackQueryHandler

from travel_agent.context import Context
from travel_agent.middlewares import middlewares
from travel_agent.utils import callback_query_callback, check_callback_data


def create_handlers() -> list[BaseHandler]:
    return [
        CallbackQueryHandler(
            build_route_of_travel,
            lambda data: check_callback_data(data, "travel_build_full_route"),
        )
    ]


@middlewares
@callback_query_callback
async def build_route_of_travel(
    callback_query: CallbackQuery, context: Context
) -> None:
    travel_id = cast(int, callback_query.data[1])
    travel = await context.travel_repo.get(travel_id)
    await callback_query.answer()

    points = [(location.lon, location.lat) for location in travel.locations]

    user = await context.user_repo.get(callback_query.from_user.id)
    if user.city and user.country:
        places = await context.map_search_repo.search(f"{user.country}, {user.city}")
        points.insert(0, (places[0].lon, places[0].lat))

    route = await context.route_repo.create_car_route(*points)

    await context.bot.send_chat_action(
        chat_id=callback_query.message.chat.id, action=ChatAction.UPLOAD_PHOTO
    )

    # TODO: staticmap uses thread pool and requests.
    # We should rewrite it for asyncio.
    route_map = staticmap.StaticMap(1024, 1024)
    route_map.add_line(staticmap.Line(route, "blue", 3))
    for point in points:
        route_map.add_marker(staticmap.CircleMarker(point, "blue", 10))
    image = route_map.render()

    with io.BytesIO() as fp:
        image.save(fp, format="png", optimize=True)
        await callback_query.message.reply_photo(fp.getvalue())
