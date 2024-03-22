import enum
from datetime import datetime

from advanced_alchemy.base import CommonTableAttributes, orm_registry
from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Table,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(CommonTableAttributes, DeclarativeBase):
    registry = orm_registry


user_to_interest_table = Table(
    "user_to_interest",
    Base.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("interest_id", ForeignKey("interest.id"), primary_key=True),
)

user_to_travel_table = Table(
    "user_to_travel",
    Base.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("travel_id", ForeignKey("travel.id"), primary_key=True),
)


class SexEnum(enum.StrEnum):
    male = enum.auto()
    female = enum.auto()


class Interest(Base):
    id: Mapped[int] = mapped_column(
        BigInteger(), primary_key=True, unique=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(unique=True)


class User(Base):
    id: Mapped[int] = mapped_column(
        BigInteger(), primary_key=True, unique=True, autoincrement=True
    )
    age: Mapped[int | None]
    sex: Mapped[SexEnum | None] = mapped_column(Enum(SexEnum))
    country: Mapped[str | None]
    city: Mapped[str | None]
    bio: Mapped[str | None]

    travels: Mapped[set["Travel"]] = relationship(
        secondary=user_to_travel_table, back_populates="users", lazy="selectin"
    )
    interests: Mapped[set[Interest]] = relationship(secondary=user_to_interest_table)


class Location(Base):
    id: Mapped[int] = mapped_column(
        BigInteger(), primary_key=True, unique=True, autoincrement=True
    )
    travel_id: Mapped[int] = mapped_column(ForeignKey("travel.id"))
    name: Mapped[str]
    lat: Mapped[float]
    lon: Mapped[float]
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Note(Base):
    id: Mapped[str] = mapped_column(primary_key=True, unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    travel_id: Mapped[int] = mapped_column(ForeignKey("travel.id"))
    is_private: Mapped[bool] = mapped_column(default=True)


class Travel(Base):
    id: Mapped[int] = mapped_column(
        BigInteger(), primary_key=True, unique=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(unique=True)
    bio: Mapped[str | None]

    users: Mapped[set[User]] = relationship(
        secondary=user_to_travel_table, back_populates="travels", lazy="selectin"
    )
    locations: Mapped[set[Location]] = relationship()
    notes: Mapped[set[Note]] = relationship()
