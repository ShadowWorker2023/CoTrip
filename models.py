# классы, описывающие сущности

class TripService:
    room_id = None  # chat_id


class Trip:
    datetime_start = ''
    datetime_finish = None
    driver = ''
    point_from = ''
    point_to = ''
    distance = None  # feature
    travel_time = None  # feature
    passengers = []  # len = driver.car_size - 1
    tag = None  # feature for trip templates

    def __init__(self):
        pass

    def __str__(self):
        return f'Поездака из {self.point_from} в {self.point_to} ' \
               f'выезд {self.datetime_start}, прибытие {self.datetime_finish}.' \
               f'Повезет {self.driver}. Текущие пассажиры: {self.passengers}.'


class User:
    tg_id = ''
    user_name = ''
    car_model = None
    car_size = ''

    def change_car(self):
        pass

