import asyncio
from datetime import datetime, timedelta
from typing import List, Set

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, ForeignKey, Table, Interval, select

Base = declarative_base()

# Таблица для связи многие ко многим между trip и user (пассажиры)
trip_passengers = Table(
    'trip_passengers',
    Base.metadata,
    mapped_column('trip_id', ForeignKey('trips.id'), primary_key=True),
    mapped_column('user_id', ForeignKey('users.id'), primary_key=True)
)


# Таблица пользователей
class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_name: Mapped[str] = mapped_column(String, nullable=False)

    trips_as_driver = relationship("Trip", back_populates="driver")
    trips_as_passenger = relationship(
        "Trip",
        secondary=trip_passengers,
        back_populates="passengers"
    )


# Таблица поездок
class Trip(Base):
    __tablename__ = 'trips'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    datetime_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    datetime_finish: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    point_from: Mapped[str] = mapped_column(String, nullable=False)
    point_to: Mapped[str] = mapped_column(String, nullable=False)
    distance: Mapped[int] = mapped_column(Integer, nullable=False)
    travel_time: Mapped[timedelta] = mapped_column(Interval, nullable=False)
    tag: Mapped[str] = mapped_column(String, nullable=True)

    driver = relationship("User", back_populates="trips_as_driver")
    passengers: Set[User] = relationship(
        "User",
        secondary=trip_passengers,
        back_populates="trips_as_passenger"
    )


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
        driver = await session.get(User, user_id)
        if not driver:
            raise ValueError("User not found")
        # Получим пассажиров
        passengers = []
        for pid in passenger_ids:
            user = await session.get(User, pid)
            if user:
                passengers.append(user)
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
            passengers=set(passengers)
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



import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, select

Base = declarative_base()

# Определение модели для таблицы trips
class Trip(Base):
    __tablename__ = 'trips'

    id = Column(Integer, primary_key=True, index=True)
    trip_name = Column(String, nullable=False)
    trip_start_point = Column(String, nullable=False)
    trip_start_time = Column(DateTime, nullable=False)
    trip_finish_point = Column(String, nullable=False)
    trip_finish_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Определение модели для таблицы statistics
class Statistic(Base):
    __tablename__ = 'statistics'

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey('trips.id'), nullable=False)
    user_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Создание асинхронного движка
DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Функция для создания таблиц
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Функция для добавления нового путешествия
async def add_trip(trip_name, start_point, start_time, finish_point, finish_time):
    async with async_session() as session:
        new_trip = Trip(
            trip_name=trip_name,
            trip_start_point=start_point,
            trip_start_time=start_time,
            trip_finish_point=finish_point,
            trip_finish_time=finish_time,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(new_trip)
        await session.commit()
        await session.refresh(new_trip)
        return new_trip

# Функция для получения всех путешествий
async def get_trips():
    async with async_session() as session:
        result = await session.execute(select(Trip))
        trips = result.scalars().all()
        return trips

# Функция для добавления статистики
async def add_statistic(trip_id, user_name):
    async with async_session() as session:
        new_stat = Statistic(
            trip_id=trip_id,
            user_name=user_name,
            created_at=datetime.utcnow()
        )
        session.add(new_stat)
        await session.commit()
        await session.refresh(new_stat)
        return new_stat

# Функция для получения статистики по trip_id
async def get_statistics(trip_id):
    async with async_session() as session:
        result = await session.execute(
            select(Statistic).where(Statistic.trip_id == trip_id)
        )
        stats = result.scalars().all()
        return stats

# Пример использования
async def main():
    await init_db()

    # Добавляем новое путешествие
    trip = await add_trip(
        trip_name="Путешествие в Москву",
        start_point="Санкт-Петербург",
        start_time=datetime(2024, 4, 27, 8, 0),
        finish_point="Москва",
        finish_time=datetime(2024, 4, 27, 20, 0)
    )
    print(f"Добавлено путешествие: {trip.id} - {trip.trip_name}")

    # Получаем все путешествия
    trips = await get_trips()
    print("Все путешествия:")
    for t in trips:
        print(f"{t.id}: {t.trip_name} от {t.trip_start_point} до {t.trip_finish_point}")

    # Добавляем статистику
    stat = await add_statistic(trip_id=trip.id, user_name="Ivan")
    print(f"Добавлена статистика: {stat.id} для trip_id {stat.trip_id}")

    # Получаем статистику по trip_id
    stats = await get_statistics(trip.id)
    print(f"Статистика для trip_id {trip.id}:")
    for s in stats:
        print(f"{s.id}: {s.user_name} в {s.created_at}")

if __name__ == "__main__":
    asyncio.run(main())