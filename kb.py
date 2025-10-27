#from aiogram.utils.keyboard import ReplyKeyboardBuilder
#from aiogram import types

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

btn_reg = KeyboardButton(text='Зарегистрироваться')

btn_stat = KeyboardButton(text='Статистика')
btn_trip = KeyboardButton(text='Создать поездку')

menu_main = ReplyKeyboardMarkup(keyboard=[[btn_trip, btn_stat]], resize_keyboard=True)

# ---- create trip KBs ------------
def make_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    """
    Создаёт реплай-клавиатуру с кнопками в один ряд
    :param items: список текстов для кнопок
    :return: объект реплай-клавиатуры
    """
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)


#----------------------------------


#@router.message(Command("functions"))
#async def main_kb_builder(message: types.Message):
#    builder = ReplyKeyboardBuilder()
#    builder.add(types.KeyboardButton(text='Создать поездку'))
#    builder.add(types.KeyboardButton(text='Статистика'))
#    # builder.adjust(4)  # строки по (n) кнопок
#    return builder.as_markup(resize_keyboard=True
#                                      #,input_field_placeholder="Выберите способ подачи"
#                                       # подсказка в поле ввода при активной клаве
#                                       )





