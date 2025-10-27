# классы, описывающие сущности
from datetime import datetime, timedelta
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class TripService:
    room_id = None  # chat_id


class Trip:
    datetime_start: Mapped[datetime]
    datetime_finish: Mapped[datetime]
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    point_from: Mapped[str]
    point_to: Mapped[str]
    distance: Mapped[int]
    travel_time: Mapped[timedelta]
    passengers = []  # len = driver.car_size - 1 #многие ко многим
    tag: Mapped[str]  # feature for trip templates

    # Связь многие-к-одному с User
    user: Mapped["User"] = relationship(
        "User",
        back_populates="trips"
    )

    def __init__(self):
        pass

    def __str__(self):
        return f'Поездака из {self.point_from} в {self.point_to} ' \
               f'выезд {self.datetime_start}, прибытие {self.datetime_finish}.' \
               f'Повезет {self.driver}. Текущие пассажиры: {self.passengers}.'


class User(Base):
    tg_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    user_name: Mapped[str] = mapped_column(String, nullable=False)  # == Mapped[str]
    car_model: Mapped[str] = mapped_column(String)  # Mapped[str | None] == mapped_column(String, nullable=True)
    car_size: Mapped[int] = mapped_column(Integer)

    trips: Mapped[list["Trips"]] = relationship(
        "Trip",
        back_populates="user",
        # cascade="all, delete-orphan"  # При удалении User удаляются и связанные Post
    )

    def change_car(self):
        pass
