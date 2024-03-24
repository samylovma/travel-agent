import enum
from datetime import date

from advanced_alchemy.base import CommonTableAttributes, orm_registry
from sqlalchemy import (
    BigInteger,
    Column,
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

    travels: Mapped[list["Travel"]] = relationship(
        secondary=user_to_travel_table,
        lazy="selectin",
        order_by="asc(Travel.id)",
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
    start_at: Mapped[date]
    end_at: Mapped[date]


class Note(Base):
    id: Mapped[str] = mapped_column(primary_key=True, unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    travel_id: Mapped[int] = mapped_column(ForeignKey("travel.id"))
    name: Mapped[str]
    is_private: Mapped[bool] = mapped_column(default=True)


class Travel(Base):
    id: Mapped[int] = mapped_column(
        BigInteger(), primary_key=True, unique=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(unique=True)
    bio: Mapped[str | None]

    locations: Mapped[list[Location]] = relationship(
        lazy="selectin", order_by="asc(Location.start_at)"
    )
    notes: Mapped[list[Note]] = relationship(lazy="selectin")
