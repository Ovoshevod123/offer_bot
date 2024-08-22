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

async def average_rating(user):
    common = 0
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"SELECT fb_score FROM fb_offer WHERE fb_user = '{user}'")
    score = cur.fetchall()
    col = len(score)
    db.commit()
    db.close()
    if col or common == 0:
        return 0, 0
    else:
        for i in score:
            common += int(i[0])
        common = int(common)/col
        return common, col

async def forward(message, id):
    try:
        db = sqlite3.connect('users.db')
        cur = db.cursor()
        cur.execute(f"SELECT * FROM users_offer WHERE offer_id_channel = '{id}'")
        name = cur.fetchall()
        db.commit()
        db.close()
        a = name[0][2]
        a = a.split('|')
        a.pop(0)
        average = await average_rating(name[0][8])
        text = f"Цена: {name[0][3]}\n{name[0][4]}\n{name[0][5]}\n{name[0][6]}\n\nПродавец: @{name[0][8]}\nРейтинг продавца: {average[0]}\nКол-во отзывов: {average[1]}"
        builder = MediaGroupBuilder(caption=text)
        for i in a:
            builder.add_photo(media=f'{i}')
        await message.answer_media_group(media=builder.build())
        return name
    except:
        return 'error'

class feedback_class_1(StatesGroup):
    id = State()

class feedback_class_2(StatesGroup):
    text_fb = State()
    score = State()

class fb_chek(StatesGroup):
    user_name = State()

async def account_fb(call, msg):
    global fb_score, fbs
    rows = [[InlineKeyboardButton(text='<', callback_data='<<'), InlineKeyboardButton(text='>', callback_data='>>')],
            [InlineKeyboardButton(text='Назад⬅️', callback_data='account')]]
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"SELECT * FROM fb_offer WHERE seller = '{msg.from_user.username}'")
    fbs = cur.fetchall()
    db.commit()
    db.close()
    fb_score = len(fbs)
    await fbs_def(call.message, fbs, 0, 'acc')

@rt_3.callback_query(F.data == 'fb_back_1')
@rt_3.callback_query(F.data == 'fb_menu')
async def menu_fb(call: CallbackQuery):
    rows = [[InlineKeyboardButton(text='Оставить отзыв', callback_data='send_fb'), InlineKeyboardButton(text='Посмотреть отзывы', callback_data='chek_fb')],
            [buttons[4]]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await call.message.edit_text(text='fb', reply_markup=markup)

@rt_3.callback_query(F.data == 'chek_fb')
async def feedback_chek_0(call: CallbackQuery, state: FSMContext):
    global fb_score_main
    rows = [[InlineKeyboardButton(text='Назад', callback_data='fb_back_1')]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await call.message.edit_text(text='Введите имя продавца (Пример: @name)', reply_markup=markup)
    await state.set_state(fb_chek.user_name)
    fb_score_main -= fb_score_main

@rt_3.callback_query(F.data == '>>')
async def feedback_chek_0(call: CallbackQuery):
    global fb_score_main
    fb_score_main += 1
    scr = fb_score_main
    await fbs_def(call.message, fbs, scr, 'acc')

@rt_3.callback_query(F.data == '<<')
async def feedback_chek_0(call: CallbackQuery):
    global fb_score_main
    if fb_score_main == 0:
        scr = fb_score_main
    else:
        fb_score_main -= 1
        scr = fb_score_main
    await fbs_def(call.message, fbs, scr, 'acc')

@rt_3.callback_query(F.data == '>')
async def feedback_chek_0(call: CallbackQuery):
    global fb_score_main
    fb_score_main += 1
    scr = fb_score_main
    await fbs_def(call.message, fbs, scr, 'fb')

@rt_3.callback_query(F.data == '<')
async def feedback_chek_0(call: CallbackQuery):
    global fb_score_main
    if fb_score_main == 0:
        scr = fb_score_main
    else:
        fb_score_main -= 1
        scr = fb_score_main
    await fbs_def(call.message, fbs, scr, 'fb')

async def fbs_def(message, data_fbs, score, out):
    if fb_score == 0:
        if out == 'fb':
            rows = [[InlineKeyboardButton(text='Назад', callback_data='chek_fb')]]
            markup = InlineKeyboardMarkup(inline_keyboard=rows)
            await message.answer(text='У этого пользователя пока что нет отзывов', reply_markup=markup)
        else:
            rows = [[InlineKeyboardButton(text='Назад⬅️', callback_data='account')]]
            markup = InlineKeyboardMarkup(inline_keyboard=rows)
            await message.edit_text(text='У вас пока что нету отзывов', reply_markup=markup)
    else:
        text = (f"Отзыв {score+1} из {fb_score}\n\n"
                f"Оценка:\n{'⭐' * data_fbs[score][3]}{' ☆' * (5 - data_fbs[score][3])}\n\n"
                f"Коментарий:\n{data_fbs[score][2]}\n\n"
                f"Дата публикации отзыва: {data_fbs[score][5]}")
        if out == 'fb':
            rows = [[InlineKeyboardButton(text='<', callback_data='<'), InlineKeyboardButton(text='>', callback_data='>')],
                    [InlineKeyboardButton(text='Назад', callback_data='chek_fb')]]
            if fb_score == 1:
                for i in range(2):
                    rows[0].pop(0)
                markup = InlineKeyboardMarkup(inline_keyboard=rows)
            elif score == 0:
                rows[0].pop(0)
                markup = InlineKeyboardMarkup(inline_keyboard=rows)
            elif score == fb_score - 1:
                rows[0].pop(1)
                markup = InlineKeyboardMarkup(inline_keyboard=rows)
            else:
                markup = InlineKeyboardMarkup(inline_keyboard=rows)
        else:
            rows = [[InlineKeyboardButton(text='<', callback_data='<<'), InlineKeyboardButton(text='>', callback_data='>>')],
                    [InlineKeyboardButton(text='Назад⬅️', callback_data='account')]]
            if fb_score == 1:
                for i in range(2):
                    rows[0].pop(0)
                markup = InlineKeyboardMarkup(inline_keyboard=rows)
            elif score == 0:
                rows[0].pop(0)
                markup = InlineKeyboardMarkup(inline_keyboard=rows)
            elif score == fb_score - 1:
                rows[0].pop(1)
                markup = InlineKeyboardMarkup(inline_keyboard=rows)
            else:
                markup = InlineKeyboardMarkup(inline_keyboard=rows)

        try:
            await message.edit_text(text=text, reply_markup=markup)
        except:
            await message.answer(text=text, reply_markup=markup)

@rt_3.message(fb_chek.user_name)
async def feedback_chek_1(message: Message, state: FSMContext):
    global fb_score, data_fb, fbs
    await state.update_data(user_name=message.text)
    rows = [[InlineKeyboardButton(text='<', callback_data='<'), InlineKeyboardButton(text='>', callback_data='>')],
            [InlineKeyboardButton(text='Назад', callback_data='chek_fb')]]
    data_fb = await state.get_data()
    data_fb = data_fb['user_name']
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"SELECT * FROM fb_offer WHERE seller = '{data_fb}'")
    fbs = cur.fetchall()
    db.commit()
    db.close()
    fb_score = len(fbs)
    await fbs_def(message, fbs, 0, 'fb')
    await state.clear()

@rt_3.callback_query(F.data == 'send_fb')
async def feedback_1(call: CallbackQuery, state: FSMContext):
    rows = [[InlineKeyboardButton(text='Назад', callback_data='fb_back_1')]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await call.message.edit_text(text='Введите id объявления', reply_markup=markup)
    await state.set_state(feedback_class_1.id)

async def feedback_1_2(message, state):
    rows = [[InlineKeyboardButton(text='Назад', callback_data='fb_back_1')]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
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
    if deff == 'error':
        await state.clear()
        await message.answer(text='Объявление не найдено')
        await feedback_1_2(message, state)
    else:
        await message.answer(text='Это объявление?', reply_markup=markup)

@rt_3.callback_query(F.data == 'fb_yes')
async def fb_data_2_1(call: CallbackQuery, bot: Bot, state: FSMContext):
    await state.clear()
    await call.message.answer(text='Напишите коментарий')
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
    await message.answer(text=f"Оценка: {data['score']}\nКометарий:   {data['text_fb']}")
    await message.answer(text=f"Все верно?", reply_markup=markup)
    await state.clear()

@rt_3.callback_query(F.data == 'publish_yes')
async def fb_data_4_1(call: CallbackQuery, bot: Bot, state: FSMContext):
    rows = [[InlineKeyboardButton(text='Главное меню', callback_data='back')]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await call.message.edit_text('Отзыв опубликован', reply_markup=markup)
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"INSERT INTO fb_offer VALUES ('{deff[0][1]}', '{deff[0][8]}', '{data['text_fb']}', '{data['score']}', '{msg.from_user.username}', '{date.today()}')")
    db.commit()
    db.close()
