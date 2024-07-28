from aiogram import types, Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery, ReplyKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from aiogram.filters import Command
from aiogram.utils.media_group import MediaGroupBuilder
import sqlite3
import time
from reply import buttons, but_del, edit_but, buttons_edit
from inf import CHANNEL_ID

rt_3 = Router()

async def forward(message, id):
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"SELECT * FROM users_offer WHERE offer_id_channel = '{id}'")
    name = cur.fetchall()
    db.commit()
    db.close()
    a = name[0][2]
    a = a.split('|')
    a.pop(0)
    text = f"Цена: {name[0][3]}\n{name[0][4]}\n{name[0][5]}\n{name[0][6]}\n\nПродавец: @{name[0][8]}\nРейтинг продавца: 4,89/5"
    builder = MediaGroupBuilder(caption=text)
    for i in a:
        builder.add_photo(media=f'{i}')
    await message.answer_media_group(media=builder.build())
    return name

class feedback_class_1(StatesGroup):
    id = State()

class feedback_class_2(StatesGroup):
    text_fb = State()
    score = State()

@rt_3.message(Command('feedback'))
async def feedback(message: Message, state: FSMContext):
    rows = [[InlineKeyboardButton(text='Главное меню', callback_data='back')]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    global send_01
    send_01 = message
    await message.answer(text='Введите id объявления', reply_markup=markup)
    await state.set_state(feedback_class_1.id)

@rt_3.message(feedback_class_1.id)
async def feedback_2(message: Message, state: FSMContext):
    global deff
    rows = [[InlineKeyboardButton(text='Да', callback_data='fb_yes'), InlineKeyboardButton(text='Нет', callback_data='fb_no')],
            [InlineKeyboardButton(text='Главное меню', callback_data='back')]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await state.update_data(id=message.text)
    data = await state.get_data()
    deff = await forward(message, data['id'])
    await message.answer(text='Это объявление?', reply_markup=markup)

@rt_3.callback_query(F.data == 'fb_yes')
async def edit_photo_2(call: CallbackQuery, bot: Bot, state: FSMContext):
    await state.clear()
    await call.message.answer(text='Напишите текст отзыва')
    await state.set_state(feedback_class_2.text_fb)

@rt_3.callback_query(F.data == 'fb_no')
async def edit_photo_2(call: CallbackQuery, bot: Bot, state: FSMContext):
    await state.clear()
    await feedback(call.message, state)

@rt_3.message(feedback_class_2.text_fb)
async def feedback_3(message: Message, state: FSMContext):
    await state.update_data(text_fb=message.text)
    await message.answer(text='Поставте оценку от 1 до 5')
    await state.set_state(feedback_class_2.score)

@rt_3.message(feedback_class_2.score)
async def feedback_4(message: Message, state: FSMContext):
    rows = [[InlineKeyboardButton(text='Опубликовать', callback_data='publish_yes'), InlineKeyboardButton(text='Заполнить отзыв занова', callback_data='publish_no')],
            [InlineKeyboardButton(text='Главное меню', callback_data='back')]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await state.update_data(score=message.text)
    data = await state.get_data()
    await message.answer(text=f"Продавец: @{deff[0][8]}\n\nОценка: {data['score']}\nТекст:   {data['text_fb']}")
    await message.answer(text=f"Все верно?", reply_markup=markup)