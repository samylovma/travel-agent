from advanced_alchemy import SQLAlchemyAsyncRepository

from .models import User


class UserRepository(SQLAlchemyAsyncRepository[User]):
    model_type = User
