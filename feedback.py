from aiogram import types, Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery, ReplyKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from aiogram.filters import Command
from aiogram.utils.media_group import MediaGroupBuilder
import sqlite3
from datetime import date
from reply import buttons, but_del, edit_but, buttons_edit
from inf import CHANNEL_ID

rt_3 = Router()
fb_score_main = 0

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

class fb_chek(StatesGroup):
    user_name = State()

@rt_3.message(Command('feedback'))
async def menu_fb(message: Message):
    rows = [[InlineKeyboardButton(text='Оставить отзыв', callback_data='send_fb'), InlineKeyboardButton(text='Посмотреть отзывы', callback_data='chek_fb')],
            [InlineKeyboardButton(text='Главное меню', callback_data='back')]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await message.answer(text='fb', reply_markup=markup)

@rt_3.callback_query(F.data == 'fb_back_1')
async def feedback_0(call: CallbackQuery, state: FSMContext):
    rows = [[InlineKeyboardButton(text='Оставить отзыв', callback_data='send_fb'), InlineKeyboardButton(text='Посмотреть отзывы', callback_data='chek_fb')],
            [InlineKeyboardButton(text='Главное меню', callback_data='back')]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await call.message.edit_text(text='fb', reply_markup=markup)
    await state.clear()

@rt_3.callback_query(F.data == 'chek_fb')
async def feedback_chek_0(call: CallbackQuery, state: FSMContext):
    rows = [[InlineKeyboardButton(text='Назад', callback_data='fb_back_1')]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await call.message.edit_text(text='Введите имя продавца (Пример: @name)')
    await state.set_state(fb_chek.user_name)

@rt_3.callback_query(F.data == '>')
async def feedback_chek_0(call: CallbackQuery):
    global fb_score_main
    rows = [[InlineKeyboardButton(text='<', callback_data='<'), InlineKeyboardButton(text='>', callback_data='>')],
            [InlineKeyboardButton(text='Назад', callback_data='chek_fb')]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    scr = fb_score_main + 1
    await fbs_def(call.message, fbs, markup, scr)

@rt_3.callback_query(F.data == '<')
async def feedback_chek_0(call: CallbackQuery):
    global fb_score_main
    rows = [[InlineKeyboardButton(text='<', callback_data='<'), InlineKeyboardButton(text='>', callback_data='>')],
            [InlineKeyboardButton(text='Назад', callback_data='chek_fb')]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    if fb_score_main == 0:
        scr = fb_score_main
    else:
        scr = fb_score_main - 1
    await fbs_def(call.message, fbs, markup, scr)

async def fbs_def(message, data_fbs, markup, score):
    try:
        text = f"Оценка: {data_fbs[score][3]}\n{data_fbs[score][2]}\n{data_fbs[score][5]}"
        await message.edit_text(text=text, reply_markup=markup)
    except:
        text = f"Оценка: {data_fbs[score][3]}\n{data_fbs[score][2]}\n{data_fbs[score][5]}"
        await message.answer(text=text, reply_markup=markup)

@rt_3.message(fb_chek.user_name)
async def feedback_chek_1(message: Message, state: FSMContext):
    global fb_score, data_fb, fbs
    await state.update_data(user_name=message.text)
    rows = [[InlineKeyboardButton(text='<', callback_data='<'), InlineKeyboardButton(text='>', callback_data='>')],
            [InlineKeyboardButton(text='Назад', callback_data='chek_fb')]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    data_fb = await state.get_data()
    data_fb = data_fb['user_name']
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"SELECT * FROM fb_offer WHERE seller = '{data_fb}'")
    fbs = cur.fetchall()
    db.commit()
    db.close()
    fb_score = len(fbs)
    await fbs_def(message, fbs, markup, 0)
    await state.clear()

@rt_3.callback_query(F.data == 'send_fb')
async def feedback_1(call: CallbackQuery, state: FSMContext):
    rows = [[InlineKeyboardButton(text='Главное меню', callback_data='back')],
            [InlineKeyboardButton(text='Назад', callback_data='fb_back_1')]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await call.message.edit_text(text='Введите id объявления', reply_markup=markup)
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
async def fb_data_2_1(call: CallbackQuery, bot: Bot, state: FSMContext):
    await state.clear()
    await call.message.answer(text='Напишите текст отзыва')
    await state.set_state(feedback_class_2.text_fb)

@rt_3.callback_query(F.data == 'fb_no')
async def fb_data_2_2(call: CallbackQuery, bot: Bot, state: FSMContext):
    await state.clear()
    await feedback_1(call, state)

@rt_3.message(feedback_class_2.text_fb)
async def feedback_3(message: Message, state: FSMContext):
    await state.update_data(text_fb=message.text)
    await message.answer(text='Поставте оценку от 1 до 5')
    await state.set_state(feedback_class_2.score)

@rt_3.message(feedback_class_2.score)
async def feedback_4(message: Message, state: FSMContext):
    global data, msg
    rows = [[InlineKeyboardButton(text='Опубликовать', callback_data='publish_yes'), InlineKeyboardButton(text='Заполнить отзыв занова', callback_data='publish_no')],
            [InlineKeyboardButton(text='Главное меню', callback_data='back')]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    msg = message
    await state.update_data(score=message.text)
    data = await state.get_data()
    await message.answer(text=f"Продавец: @{deff[0][8]}\n\nОценка: {data['score']}\nТекст:   {data['text_fb']}")
    await message.answer(text=f"Все верно?", reply_markup=markup)
    await state.clear()

@rt_3.callback_query(F.data == 'publish_yes')
async def fb_data_4_1(call: CallbackQuery, bot: Bot, state: FSMContext):
    await call.message.answer('Отзыв опубликован')
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"INSERT INTO fb_offer VALUES ('{deff[0][1]}', '{deff[0][8]}', '{data['text_fb']}', '{data['score']}', '{msg.from_user.username}', '{date.today()}')")
    db.commit()
    db.close()
