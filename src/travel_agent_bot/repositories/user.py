from sqlalchemy.ext.asyncio import AsyncSession

from ..models import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, id: int) -> User | None:
        return await self.session.get(User, id)

    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.commit()
        return user

    async def update(self, updated_user: User) -> None:
        await self.session.merge(updated_user)
        await self.session.commit()
