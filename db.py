import asyncio
from datetime import datetime, timedelta
from typing import List, Set
import enum

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, relationship, Mapped, mapped_column, declared_attr
from sqlalchemy import Integer, String, DateTime, ForeignKey, Interval, select, func
from sqlalchemy.ext.asyncio import AsyncAttrs


class RoleEnum(str, enum.Enum):
    driver = "водитель"
    passenger = "пассажир"


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True  # Класс абстрактный, чтобы не создавать отдельную таблицу для него

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + 's'


# Таблица пользователей
class User(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_name: Mapped[str] = mapped_column(String, nullable=False)


# Таблица поездок
class Trip(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    datetime_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    datetime_finish: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    point_from: Mapped[str] = mapped_column(String, nullable=False)
    point_to: Mapped[str] = mapped_column(String, nullable=False)
    distance: Mapped[int] = mapped_column(Integer, nullable=False)
    travel_time: Mapped[timedelta] = mapped_column(Interval, nullable=False)
    tag: Mapped[str] = mapped_column(String, nullable=True)


class UsersTripsLink(Base):
    user_id: Mapped[int]
    trip_id: Mapped[int]
    role: Mapped[RoleEnum]  # enum driver or passanger



# Создание асинхронного движка
DATABASE_URL = "sqlite+aiosqlite:///./test_db.db"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


# Инициализация базы данных
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Добавление пользователя
async def add_user(user_name: str) -> User:
    async with async_session() as session:
        user = User(user_name=user_name)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


# Добавление новой поездки
async def add_trip(
    datetime_start: datetime,
    datetime_finish: datetime,
    user_id: int,
    point_from: str,
    point_to: str,
    distance: int,
    travel_time: timedelta,
    tag: str,
    passenger_ids: List[int]
) -> Trip:
    async with async_session() as session:
        # Получим пользователя-водителя
        driver = user_id#await session.get(User, user_id)
        #if not driver:
        #    raise ValueError("User not found")
        # Получим пассажиров
        passengers = []
        for pid in passenger_ids:
            user = await session.get(User, pid)
            if user:
                passengers.append(user.id)
        new_trip = Trip(
            datetime_start=datetime_start,
            datetime_finish=datetime_finish,
            user_id=user_id,
            point_from=point_from,
            point_to=point_to,
            distance=distance,
            travel_time=travel_time,
            tag=tag,
            driver=driver,
            passengers=passengers#set(passengers)
        )
        session.add(new_trip)
        await session.commit()
        await session.refresh(new_trip)
        return new_trip


# Получение всех поездок
async def get_trips():
    async with async_session() as session:
        result = await session.execute(select(Trip))
        trips = result.scalars().all()
        return trips


# Получение пассажиров для конкретной поездки
async def get_passengers(trip_id: int) -> List[User]:
    async with async_session() as session:
        trip = await session.get(Trip, trip_id)
        if trip:
            return list(trip.passengers)
        return []


# Пример использования
async def main():
    await init_db()

    # Создаем пользователей
    user1 = await add_user("Ivan")
    user2 = await add_user("Anna")
    user3 = await add_user("Sergey")

    # Добавляем поездку с пассажирами
    trip = await add_trip(
        datetime_start=datetime(2024, 4, 27, 8, 0),
        datetime_finish=datetime(2024, 4, 27, 10, 0),
        user_id=user1.id,
        point_from="Санкт-Петербург",
        point_to="Москва",
        distance=700,
        travel_time=timedelta(hours=2),
        tag="business",
        passenger_ids=[user2.id, user3.id]
    )
    print(f"Добавлена поездка: {trip.id} от {trip.point_from} до {trip.point_to}")

    # Получение всех поездок
    trips = await get_trips()
    for t in trips:
        print(f"Trip {t.id} от {t.point_from} до {t.point_to}, водитель: {t.driver.user_name}")

    # Получение пассажиров
    passengers = await get_passengers(trip.id)
    print("Пассажиры:")
    for p in passengers:
        print(p.user_name)


if __name__ == "__main__":
    asyncio.run(main())
