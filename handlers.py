from aiogram import types, F, Router
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

import kb
import states
from kb import menu_main
from models import DB
import utils


router = Router()
database = DB()
database.init_db()


@router.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Привет! Здесь ты можешь создать поездку и найти себе попутчиков")
    await message.answer(
        "Выберите действие:",
        reply_markup=menu_main,)


@router.message(Command("dice"))
async def cmd_dice(message: types.Message):
    await message.answer_dice(emoji="🎲")

# ------------------------ create trip ----------------------------
trip_name_templates = ['На работу', 'другой шаблон']
trip_start_time_templates = ['Завтра 7:20', '...']
trip_start_point_templates = ['60ка 25Б', '60ка 25А', 'Бриз']
trip_finish_time_templates = ['Как получится', '...']
trip_finish_point_templates = ['Работа', 'Дом']

#@router.message(F.text.lower() == "создать поездку")
#async def with_puree(message: types.Message):
#    await message.reply("здесь должен произойти след шаг сценария")
@router.message(StateFilter(None), F.text.lower() == "создать поездку")
async def trip(message: Message, state: FSMContext):
    await message.answer(
        text="Введите название поездки или выбирите из шаблонов:",
        reply_markup=kb.make_row_keyboard(trip_name_templates)
    )
    # Устанавливаем пользователю состояние "выбирает название"
    await state.set_state(states.CreateTrip.choosing_trip_name)


@router.message(
    states.CreateTrip.choosing_trip_name,
    #F.text.in_(trip_templates) выбор только выриантв из списка
)
async def trip_name_chosen(message: Message, state: FSMContext):
    await state.update_data(trip_name=message.text.lower())  # TODO валидация данных мб через pydantic
    await message.answer(
        text="Отлично. Теперь, выберите время поездки:",
        reply_markup=kb.make_row_keyboard(trip_start_time_templates)
    )
    await state.set_state(states.CreateTrip.choosing_trip_start_time)


@router.message(
    states.CreateTrip.choosing_trip_start_time,
    #F.text.in_(trip_templates) выбор только выриантв из списка
)
async def trip_start_time_chosen(message: Message, state: FSMContext):
    await state.update_data(trip_start_time=message.text.lower())
    await message.answer(
        text="Отлично. Теперь, выберите место старта поездки:",
        reply_markup=kb.make_row_keyboard(trip_start_point_templates)
    )
    await state.set_state(states.CreateTrip.choosing_trip_start_point)


@router.message(
    states.CreateTrip.choosing_trip_start_point,
    #F.text.in_(trip_templates) выбор только выриантв из списка
)
async def trip_start_point_chosen(message: Message, state: FSMContext):
    await state.update_data(trip_start_point=message.text.lower())
    await message.answer(
        text="Отлично. Теперь, выберите время окончания поездки:",
        reply_markup=kb.make_row_keyboard(trip_finish_time_templates)
    )
    await state.set_state(states.CreateTrip.choosing_trip_finish_time)


@router.message(
    states.CreateTrip.choosing_trip_finish_time,
    #F.text.in_(trip_templates) выбор только выриантв из списка
)
async def trip_finish_time_chosen(message: Message, state: FSMContext):
    await state.update_data(trip_finish_point=message.text.lower())
    await message.answer(
        text="Отлично. Теперь, выберите место окончания поездки:",
        reply_markup=kb.make_row_keyboard(trip_finish_point_templates)
    )
    await state.set_state(states.CreateTrip.choosing_trip_finish_point)


# last state
@router.message(states.CreateTrip.choosing_trip_finish_point,
                #F.text.in_(available_food_sizes)
                )
async def trip_finish_point_chosen(message: Message, state: FSMContext):
    await state.update_data(trip_finish_time=message.text.lower())
    user_data = await state.get_data()  # TODO передача данных на создание модели, храниение в бд статистики
    await database.add_trip(datetime_start=utils.convert_str_to_dt(user_data['trip_start_time']),
                            datetime_finish=utils.convert_str_to_dt(user_data['trip_finish_time']),
                            user_id=message.from_user.id,
                            point_from=user_data['trip_start_point'],
                            point_to=user_data['trip_finish_point'],
                            )
    await message.answer(
        text=f"Вы создали поездку '{user_data['trip_name']}' "
             f"старт: {user_data['trip_start_point']} в {user_data['trip_start_time']} "
             f"финиш: {user_data['trip_finish_point']} в {user_data['trip_finish_time']}.",
        reply_markup=menu_main  # ReplyKeyboardRemove()  # or man_menu_kb
    )
    await state.clear()  # in last state TODO создание инлайн панели с бронированем мест и тд
#------------------------------------------------------------------

@router.message(F.text.lower() == "статистика")
async def without_puree(message: types.Message):
    await message.reply("список с цифрами")


#@router.message()
#async def message_handler(message: types.Message):
#    await message.answer(f"Твой ID: {message.from_user.id}")
