from advanced_alchemy import SQLAlchemyAsyncRepository

from travel_agent.models import User


class UserRepository(SQLAlchemyAsyncRepository[User]):
    model_type = User
