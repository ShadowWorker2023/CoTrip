import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
import enum

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Mapped, mapped_column, declared_attr
from sqlalchemy import Integer, String, DateTime, Interval, select, func
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
    # and other params


# Таблица поездок
class Trip(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    datetime_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    datetime_finish: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    #user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    point_from: Mapped[str] = mapped_column(String, nullable=False)
    point_to: Mapped[str] = mapped_column(String, nullable=False)
    distance: Mapped[int] = mapped_column(Integer, nullable=False)
    travel_time: Mapped[timedelta] = mapped_column(Interval, nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    tag: Mapped[str] = mapped_column(String, nullable=True)


class UsersTripsLink(Base):
    user_id: Mapped[int]
    trip_id: Mapped[int]
    role: Mapped[RoleEnum]  # enum driver or passanger


class DB:
    engine: Any
    async_session: Any
    base: Any

    def __init__(self):
        # Создание асинхронного движка
        DATABASE_URL = "sqlite+aiosqlite:///./test_db.db"

        self.engine = create_async_engine(DATABASE_URL, echo=True)
        self.async_session = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)

        self.base = Base

    # Инициализация базы данных
    async def init_db(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(self.base.metadata.create_all)

    # Добавление пользователя
    async def add_user(self, user_name: str) -> User:
        async with self.async_session() as session:
            user = User(user_name=user_name)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    # Добавление новой поездки
    async def add_trip(self,
                       datetime_start: datetime,
                       datetime_finish: datetime,
                       user_id: int,
                       point_from: str,
                       point_to: str,
                       distance: int,
                       travel_time: timedelta,
                       tag: str,
                       passenger_ids: List[int],
                       price: int = 0
                       ) -> Trip:
        async with self.async_session() as session:
            new_trip = Trip(
                datetime_start=datetime_start,
                datetime_finish=datetime_finish,
                #user_id=user_id,
                point_from=point_from,
                point_to=point_to,
                distance=distance,
                travel_time=travel_time,
                price=price,
                tag=tag,
            )
            session.add(new_trip)
            await session.commit()
            await session.refresh(new_trip)
            # добавим в link таблицу записи о driver, passengers
            session.add(UsersTripsLink(user_id=user_id,
                                       trip_id=new_trip.id,
                                       role=RoleEnum.driver))
            for passenger_id in passenger_ids:
                session.add(UsersTripsLink(user_id=passenger_id,
                                           trip_id=new_trip.id,
                                           role=RoleEnum.passenger))
            await session.commit()
            return new_trip

    # Получение всех поездок
    async def get_trips(self):
        async with self.async_session() as session:
            result = await session.execute(select(Trip))
            trips = result.scalars().all()
            return trips

    # Получение пассажиров и водителя для конкретной поездки
    async def get_users_by_trip(self, trip: Trip | int) -> Dict:
        if isinstance(trip, Trip):
            pass
        elif isinstance(trip, int):
            async with self.async_session() as session:
                trip = await session.get(Trip, trip)
        else:
            # another class
            pass
        async with self.async_session() as session:
            res = await session.execute(select(UsersTripsLink.user_id).filter(UsersTripsLink.trip_id == trip.id,
                                     UsersTripsLink.role == RoleEnum.driver))
            driver_id = res.first()[0]
            driver = await session.get(User, driver_id)

            result = await session.execute(select(UsersTripsLink.user_id).filter(UsersTripsLink.trip_id == trip.id,
                                                                         UsersTripsLink.role == RoleEnum.passenger))
            passenger_ids = result.scalars().all()
            result2 = await session.execute(select(User).where(User.id.in_(passenger_ids)))
            passengers = result2.scalars().all()

            return {'driver': driver, 'passengers': passengers}


# Пример использования
async def main():

    database = DB()
    await database.init_db()

    # Создаем пользователей
    user1 = await database.add_user("Ivan")
    user2 = await database.add_user("Anna")
    user3 = await database.add_user("Sergey")

    # Добавляем поездку с пассажирами
    trip = await database.add_trip(
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
    trips = await database.get_trips()
    for t in trips:
        users = await database.get_users_by_trip(t)
        print(f"Trip {t.id} от {t.point_from} до {t.point_to}, "
              f"водитель: {users.get('driver').user_name}, "
              f"пассажиры: {[user.user_name for user in users.get('passengers')]}")


if __name__ == "__main__":
    asyncio.run(main())
