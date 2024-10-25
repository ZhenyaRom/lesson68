from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from crud_functions import *

api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())
kb1 = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Регистрация')],
        [KeyboardButton(text='Рассчитать'),
         KeyboardButton(text='Информация')],
        [KeyboardButton(text='Купить')]
    ], resize_keyboard=True
)

kb_in = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories'),
         InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')]
    ]
)

kb_buy_in = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Напиток арбузный', callback_data='product_buying')],
        [InlineKeyboardButton(text='Напиток грушевый', callback_data='product_buying')],
        [InlineKeyboardButton(text='Напиток земляничный', callback_data='product_buying')],
        [InlineKeyboardButton(text='Напиток яблочный', callback_data='product_buying')]
    ]
)


class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()


@dp.message_handler(text='Регистрация')
async def sing_up(message):
    await message.answer("Введите имя пользователя (только латинский алфавит):")
    await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    username_error = False
    for i in message.text:
        if 65 > ord(i) or ord(i) > 122 or 90 < ord(i) < 97:
            username_error = True
            break
    if username_error:
        await message.answer("Некорректный ввод.")
        await message.answer("Введите имя пользователя (только латинский алфавит)")
        await RegistrationState.username.set()
    else:
        if is_included(message.text):
            await message.answer("Пользователь существует, введите другое имя")
            await RegistrationState.username.set()
        else:
            await state.update_data(username=message.text)
            await message.answer("Введите свой email:")
            await RegistrationState.email.set()


@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    await state.update_data(email=message.text)
    await message.answer("Введите свой возраст:")
    await RegistrationState.age.set()


@dp.message_handler(state=RegistrationState.age)
async def set_age(message, state):
    if not message.text.isnumeric():
        await message.answer("Некорректный ввод.")
        await message.answer("Введите свой возраст:")
        await RegistrationState.age.set()
    elif 120 < int(message.text):
        await message.answer("Некорректный ввод.")
        await message.answer("Введите свой возраст:")
        await RegistrationState.age.set()
    else:
        await state.update_data(age=message.text)
        data = await state.get_data()
        add_user(data['username'], data['email'], data['age'])
        await message.answer("Регистрация прошла успешно")
        await state.finish()


@dp.message_handler(text='Информация')
async def info(message):
    await message.answer('рассчитываю суточную норму калорий на основании вашего возраста, роста и веса',
                         reply_markup=kb1)


@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию: ', reply_markup=kb_in)


@dp.message_handler(text='Купить')
async def get_buying_list(message):
    all_products = get_all_products()
    for product in all_products:
        with open(product[4], 'rb') as img:
            await message.answer_photo(img, f'Название: {product[1]} | Описание: {product[2]} | Цена: {product[3]}')

    await message.answer('Выберите продукт для покупки:', reply_markup=kb_buy_in)


@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('calories = 10 * вес + 6.25 * рост - 5 * возраст - 161')
    await call.answer()


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст: ')
    await call.answer()
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост: ')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес: ')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    try:
        c = 10 * int(data['weight']) + 6.25 * int(data['growth']) - 5 * int(data['age']) - 161
        await message.answer(f'Ваша норма калорий - {c}')
    except ValueError:
        await message.answer('Возраст, рост и вес нухно вводить арабскими цифрами', reply_markup=kb1)
    await state.finish()


@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')
    await call.answer()


@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer('Привет! Я бот помогающий твоему здоровью.', reply_markup=kb1)


@dp.message_handler()
async def all_massages(message):
    await message.answer('Введите команду /start, чтобы начать общение.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
