from aiogram.fsm.state import StatesGroup, State


# kонечный автомат создания поездки
class CreateTrip(StatesGroup):
    # название поездки (в том числе готовые tags #work ...)
    choosing_trip_name = State()
    # время старта
    choosing_trip_start_time = State()
    # время финиша ? *с возможностью пропустить
    choosing_trip_finish_time = State()
    # место отправления
    choosing_trip_start_point = State()
    # место прибытия * пропускается при выборе шаблона
    choosing_trip_finish_point = State()

