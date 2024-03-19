from advanced_alchemy import SQLAlchemyAsyncRepository

from travel_agent.models import Travel, User


class UserRepository(SQLAlchemyAsyncRepository[User]):
    model_type = User


class TravelRepository(SQLAlchemyAsyncRepository[Travel]):
    model_type = Travel
