from aiogram import types, F, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder


router = Router()


@router.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Привет! Я помогу тебе узнать твой ID, просто отправь мне любое сообщение")


@router.message(Command("dice"))
async def cmd_dice(message: types.Message):
    await message.answer_dice(emoji="🎲")


@router.message(Command("functions"))
async def functions_builder(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text='Создать поездку'))
    builder.add(types.KeyboardButton(text='Статистика'))
    # builder.adjust(4)  # строки по (n) кнопок
    await message.answer(
        "Выберите действие:",
        reply_markup=builder.as_markup(resize_keyboard=True
                                       #,input_field_placeholder="Выберите способ подачи"
                                       # подсказка в поле ввода при активной клаве
                                       ),
    )


@router.message(F.text.lower() == "создать поездку")
async def with_puree(message: types.Message):
    await message.reply("здесь должен произойти след шаг сценария")


@router.message(F.text.lower() == "статистика")
async def without_puree(message: types.Message):
    await message.reply("список с цифрами")


@router.message()
async def message_handler(message: types.Message):
    await message.answer(f"Твой ID: {message.from_user.id}")
