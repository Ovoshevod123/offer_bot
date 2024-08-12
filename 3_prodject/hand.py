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
from feedback import average_rating

rt = Router()

photo = []
id_list = []
id_list_pay = []

class new_product(StatesGroup):
    photo = State()
    name = State()
    description = State()
    price = State()
    locate = State()

@rt.message(Command('start'))
async def start(message: Message):
    global send_01
    rows = [[buttons[5], buttons[1]],
            [buttons[6], buttons[0]]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await message.answer(text='Здравсвуйте', reply_markup=markup)
    send_01 = message

@rt.callback_query(F.data == 'back')
async def back(call: CallbackQuery, state: FSMContext):
    global id_list, id_list_pay
    rows = [[buttons[5], buttons[1]],
            [buttons[6], buttons[0]]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await call.message.edit_text(text='Здравсвуйте', reply_markup=markup)
    await state.clear()
    id_list.clear()
    id_list_pay.clear()

@rt.callback_query(F.data == 'new')
async def new_1(callback: CallbackQuery, state: FSMContext):
    photo.clear()
    rows = [[buttons[4]]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await callback.message.edit_text(text=f'Вы начали заполнение анкеты нового товара.\n\nПришлите фото:', reply_markup=markup)
    await state.set_state(new_product.photo)

@rt.message(new_product.photo)
async def new_2(message: Message, state: FSMContext):
    kb = [[types.KeyboardButton(text="Это все, сохранить фото")]]
    markup = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    try:
        if message.text == 'Это все, сохранить фото':
            await state.update_data(photo=photo)
            await state.set_state(new_product.name)
            await message.answer(text='Фото сохранены.', reply_markup=types.ReplyKeyboardRemove())
            await message.answer(text='Введите название товара:')

        else:
            photo_1 = message.photo
            photo.append(photo_1[-1].file_id)
            col = len(photo)
            if col == 5:
                await message.answer(text='Фото добавлено – 5 из 5', reply_markup=types.ReplyKeyboardRemove())
                await message.answer(text='Введите название товара:', reply_markup=types.ReplyKeyboardRemove())
                await state.update_data(photo=photo)
                await state.set_state(new_product.name)
            elif col > 5:
                await message.answer(text='Вы отправили больше 5 фото')
            else:
                await message.answer(text=f'Фото добавлено – {col} из 5. Еще одно?', reply_markup=markup)
    except TypeError:
        await message.answer(text='Пришлите фото!')

@rt.message(new_product.name)
async def new_3(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(new_product.description)
    await message.answer(text='Введите описание товара:')

@rt.message(new_product.description)
async def new_4(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(new_product.price)
    await message.answer(text='Введите цену товара:')

@rt.message(new_product.price)
async def new_5(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    await state.set_state(new_product.locate)
    await message.answer(text='Укажите место встречи с покупателем:')

@rt.message(new_product.locate)
async def new_6(message: Message, state: FSMContext, bot: Bot, ):
    await state.update_data(locate=message.text)
    data = await state.get_data()
    global text, send, name_ofer, data_state
    data_state = data
    average = await average_rating(message.from_user.username)
    text = f"Цена: {data['price']}\n{data['name']}\n{data['description']}\n{data['locate']}\n\nПродавец: @{message.from_user.username}\nРейтинг продавца: {average[0]}\nКол-во отзывов: {average[1]}"
    builder = MediaGroupBuilder(caption=text)
    for i in data['photo']:
        builder.add_photo(media=f'{i}')
    send = await message.answer_media_group(media=builder.build())
    rows = [[buttons[2]],
            [buttons[3]]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await message.answer(text='Вот так будет выглядить твое объяевление.\n\nПроверь что все выглядит правильно!\n', reply_markup=markup)
    if message.from_user.username == None:
        await message.answer('У тебя нету публичного username, из за этого пользователи не смогут перейти в твой профиль и написать тебе(\n\nПерейди в настройки Telegram и создай свой публичный username')
    name_ofer = data['name']
    await state.clear()

@rt.callback_query(F.data == 'good')
async def send_0(callback: CallbackQuery, bot: Bot):
    global send_01, send_02
    rows = [[buttons[4]]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    col = len(photo)
    if col > 1:
        media = [
            types.InputMediaPhoto(media=photo[0], caption=text),
            *[types.InputMediaPhoto(media=photo_id) for photo_id in photo[1:]]
        ]
    else:
        media = [types.InputMediaPhoto(media=photo[0], caption=text)]

    send_02 = await bot.send_media_group(chat_id=CHANNEL_ID, media=media)
    await bot.edit_message_caption(chat_id=CHANNEL_ID, message_id=send_02[0].message_id, caption=text + f'\nid сообщения: {send_02[0].message_id}')
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    a = ''
    for i in data_state['photo']:
        a = a+'|'+i

    cur.execute(f"SELECT id FROM users WHERE id = '{send_01.from_user.id}'")
    info = cur.fetchone()
    if info == None:
        cur.execute(f"INSERT INTO users VALUES ('{send_01.from_user.id}', '{send_01.from_user.username}', '{send_01.from_user.full_name}')")
    cur.execute(f"""INSERT INTO users_offer VALUES ('{send_01.chat.id}', '{send_02[0].message_id}', '{a}', '{data_state['name']}', '{data_state['description']}', '{data_state['price']}', '{data_state['locate']}', '{send_02[0].media_group_id}', '{send_01.from_user.username}')""")
    db.commit()
    db.close()

    await callback.message.edit_text(text='Теперь твое объявление опубликованно <a href="https://web.telegram.org/a/#-1002160209777">здесь</a>.', parse_mode='HTML', reply_markup=markup)
    photo.clear()

def offer_def(msg, from_var):
    global id_list, deff, id_list_pay

    deff = but_del(msg, from_var)
    if from_var == 'menu':
        for i in deff[1].keys():
            id_list.append(f'{i[0]}_menu')
    if from_var == 'pay':
        for i in deff[1].keys():
            id_list_pay.append(f'{i[0]}_pay')
    row = deff[0]
    return row

@rt.callback_query(F.data == 'menu')
async def delete_0(call: CallbackQuery):
    rows = offer_def(call.message, 'menu')
    rows_2 = [[buttons[0]],
              [buttons[4]]]
    if len(rows) == 1:
        markup = InlineKeyboardMarkup(inline_keyboard=rows_2)
        await call.message.edit_text(text='У вас нет активных объявлений(\n\nХотите создать новое объявление?', reply_markup=markup)
    else:
        markup = InlineKeyboardMarkup(inline_keyboard=rows)
        await call.message.edit_text(text='Выберите товар:', reply_markup=markup)

async def forward(message, offer_data):
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"SELECT * FROM users_offer WHERE offer_id_channel = '{offer_data}'")
    name = cur.fetchall()
    db.commit()
    db.close()
    a = name[0][2]
    a = a.split('|')
    a.pop(0)
    average = await average_rating(name[0][8])
    text = f"Цена: {name[0][3]}\n{name[0][4]}\n{name[0][5]}\n{name[0][6]}\nПродавец: @{name[0][8]}\nРейтинг продавца: {average[0]}\nКол-во отзывов: {average[1]}"
    builder = MediaGroupBuilder(caption=text)
    for i in a:
        builder.add_photo(media=f'{i}')
    id_msg = await message.answer_media_group(media=builder.build())
    return id_msg

async def del_media(bot, id_offer):
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"SELECT photo FROM users_offer WHERE offer_id_channel = '{id_offer}'")
    photo_ = cur.fetchone()
    db.commit()
    db.close()
    photo_ = photo_[0]
    photo_ = photo_.split('|')
    photo_.pop(0)
    col = len(photo_)
    for i in range(col):
        ii = int(id_offer) + col - 1
        ii = ii - i
        await bot.delete_message(chat_id=CHANNEL_ID, message_id=ii)

@rt.callback_query(lambda query: query.data in id_list)
async def delete_1(call: CallbackQuery, bot: Bot):
    global call_data, call_inf, id_msg_2, id_list
    await call.message.delete()
    id_list.clear()
    call_data = call.data
    call_data = call_data.replace('_menu', '')
    call_inf = call
    id_msg_2 = await forward(call.message, call_data)
    rows = [[edit_but[0], edit_but[1]],
            [edit_but[2]]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await call.message.answer(text='Это ваше объявление⬆️\n\nЧто хотите сделать?', reply_markup=markup)

@rt.callback_query(F.data == 'back_2')
async def back_edit(call: CallbackQuery, bot: Bot):
    await delete_0(call)

@rt.callback_query(F.data == 'dell')
async def del_1(call: CallbackQuery):
    rows = [[InlineKeyboardButton(text='Продал в барахолке "название"', callback_data='sell'), InlineKeyboardButton(text='Другая причина', callback_data='dell_2')],
            [InlineKeyboardButton(text='Назад', callback_data='menu')]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await call.message.edit_text(text='Укажити причину удаления сообщения', reply_markup=markup)

@rt.callback_query(F.data == 'sell')
async def del_1(call: CallbackQuery):
    pass

@rt.callback_query(F.data == 'dell_2')
async def del_1(call: CallbackQuery):
    rows = [[InlineKeyboardButton(text='Да', callback_data='yes'), InlineKeyboardButton(text='Нет', callback_data='no')]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await call.message.edit_text(text='Вы уверены что хотите удалить объявление', reply_markup=markup)

@rt.callback_query(F.data == 'yes')
async def back_edit(call: CallbackQuery, bot: Bot):
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"SELECT photo FROM users_offer WHERE offer_id_channel = '{call_data}'")
    photo_ = cur.fetchone()
    cur.execute(f"DELETE from users_offer WHERE offer_id_channel = {call_data}")
    db.commit()
    db.close()
    photo_ = photo_[0]
    photo_ = photo_.split('|')
    photo_.pop(0)
    col = len(photo_)
    for i in range(col):
        ii = int(call_data) + col-1
        ii = ii - i
        await bot.delete_message(chat_id=CHANNEL_ID, message_id=ii)

    await call.message.edit_text(text='Объявление удалено.')
    time.sleep(1.5)
    await delete_0(call)

@rt.callback_query(F.data == 'no')
async def back_edit(call: CallbackQuery):
    rows = [[edit_but[0], edit_but[1]],
            [edit_but[2]]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await call.message.edit_text(text='Это ваше объявление⬆️\n\nЧто хотите сделать?', reply_markup=markup)

@rt.callback_query(F.data == 'edit')
async def edit_0(call: CallbackQuery):
    rows = [[buttons_edit[0]],
            [buttons_edit[1]],
            [buttons_edit[2]],
            [buttons_edit[3]],
            [buttons_edit[4]],]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await call.message.edit_text(text='Что хотите изменить?', reply_markup=markup)

class edit_product(StatesGroup):
    photo = State()
    name = State()
    description = State()
    price = State()
    locate = State()

async def edit_def(a, b, c):
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"Update users_offer set {a} = '{b}' where offer_id_channel = '{c}'")
    db.commit()
    db.close()

async def edit_media(message: Message, bot: Bot):
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"SELECT * FROM users_offer WHERE offer_id_channel = '{call_data}'")
    name = cur.fetchall()
    db.commit()
    db.close()
    a = name[0][2]
    a = a.split('|')
    a.pop(0)
    average = await average_rating(name[0][8])
    text = f"Цена: {name[0][3]}\n{name[0][4]}\n{name[0][5]}\n{name[0][6]}\nПродавец: @{name[0][8]}\nРейтинг продавца: {average[0]}\nКол-во отзывов: {average[1]}"
    builder = MediaGroupBuilder(caption=text)
    for i in a:
        builder.add_photo(media=f'{i}')
    b = await message.answer_media_group(media=builder.build())
    return a, b

@rt.callback_query(F.data == 'photo')
async def edit_photo(call: CallbackQuery, state: FSMContext, bot: Bot):
    global col_photos
    photo.clear()
    rows = [[buttons[4]]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)

    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"SELECT photo FROM users_offer WHERE offer_id_channel = '{call_data}'")
    name = cur.fetchall()
    col_photos = name[0][0].split('|')
    col_photos.pop(0)
    col_photos = len(col_photos)
    db.commit()
    db.close()

    await call.message.edit_text(text=f'Вы начали заполнение анкеты нового товара.\n\nПришлите фото:', reply_markup=markup)
    await state.set_state(edit_product.photo)

@rt.message(edit_product.photo)
async def edit_photo_2(message: Message, state: FSMContext, bot: Bot):
    global send_media_msg, gl_data
    kb = [[types.KeyboardButton(text="Это все, сохранить фото")]]
    markup = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    but = [[types.InlineKeyboardButton(text="Внести изменения", callback_data='edit_yes')]]
    markup_2 = InlineKeyboardMarkup(inline_keyboard=but)
    try:
        if message.text == 'Это все, сохранить фото':
            await state.update_data(photo=photo)
            data = await state.get_data()
            gl_data = data

            a = ''
            for i in data['photo']:
                a = a + '|' + i
            await edit_def('photo', a, call_data)
            send_media_msg = await edit_media(message, bot)
            await message.answer(text='Вот так теперь выглядит ваше объявление⬆️⬆', reply_markup=markup_2)
            await state.clear()
        else:
            photo_1 = message.photo
            photo.append(photo_1[-1].file_id)
            col = len(photo)
            if col == col_photos:
                await message.answer(text=f'Фото добавлено – {col_photos} из {col_photos}', reply_markup=types.ReplyKeyboardRemove())
                await state.update_data(photo=photo)
                data = await state.get_data()

                gl_data = data
                edit_photo_list = ''
                for i in data['photo']:
                    edit_photo_list = edit_photo_list + '|' + i
                await edit_def('photo', edit_photo_list, call_data)
                send_media_msg = await edit_media(message, bot)
                await message.answer(text='Вот так теперь выглядит ваше объявление⬆️', reply_markup=markup_2)
                await state.clear()
            elif col > col_photos:
                await message.answer(text='Вы отправили больше {col_photos} фото')
            else:
                await message.answer(text=f'Фото добавлено – {col} из {col_photos}. Еще одно?', reply_markup=markup)
    except TypeError:
            await message.answer(text='Пришлите фото!')

@rt.callback_query(F.data == 'edit_yes')
async def edit_photo_2(call: CallbackQuery, bot: Bot):
    rows = [[buttons[0], buttons[1]]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    col = len(photo)
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"SELECT * FROM users_offer WHERE offer_id_channel = '{call_data}'")
    name = cur.fetchall()
    db.commit()
    db.close()
    average = await average_rating(name[0][8])
    text = f"Цена: {name[0][4]}\n{name[0][3]}\n{name[0][5]}\n{name[0][6]}\nПродавец: @{name[0][8]}\nРейтинг продавца: {average[0]}\nКол-во отзывов: {average[1]}"
    a = name[0][2]
    a = a.split('|')
    a.pop(0)
    iii = 0
    for photos in a:
        ii = int(call_data) + iii
        iii = iii + 1
        if ii == int(call_data):
            await bot.edit_message_media(media=InputMediaPhoto(media=photos, caption=text), chat_id=CHANNEL_ID, message_id=ii)
        else:
            await bot.edit_message_media(media=InputMediaPhoto(media=photos), chat_id=CHANNEL_ID, message_id=ii)
    del iii
    if len(a) < col_photos:
        for i in range(col_photos - len(a)):
            col = int(call_data) + int(col_photos) - 1 - i
            await bot.delete_message(chat_id=CHANNEL_ID, message_id=col)

    await call.message.edit_text(text='Теперь твое объявление опубликованно <a href="https://t.me/jxddkcj">здесь</a>.', parse_mode='HTML', reply_markup=markup)
    photo.clear()

@rt.callback_query(F.data == 'edit_yes_text')
async def edit_photo_2(call: CallbackQuery, bot: Bot):
    rows = [[buttons[0], buttons[1]]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"SELECT * FROM users_offer WHERE offer_id_channel = '{call_data}'")
    name = cur.fetchall()
    db.commit()
    db.close()
    average = await average_rating(name[0][8])
    text = f"Цена: {name[0][5]}\n{name[0][3]}\n{name[0][4]}\n{name[0][6]}\nПродавец: @{name[0][8]}\nРейтинг продавца: {average[0]}\nКол-во отзывов: {average[1]}"
    await bot.edit_message_caption(chat_id=CHANNEL_ID, message_id=call_data, caption=text)
    await call.message.edit_text(text='Теперь твое объявление опубликованно <a href="https://t.me/jxddkcj">здесь</a>.',
                                 parse_mode='HTML', reply_markup=markup)

async def send_media(message):

    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"SELECT * FROM users_offer WHERE offer_id_channel = '{call_data}'")
    name = cur.fetchall()
    db.commit()
    db.close()
    name = name[0]
    a = name[2]
    a = a.split('|')
    a.pop(0)
    average = await average_rating(name[8])
    text = f"Цена: {name[5]}\n{name[3]}\n{name[4]}\n{name[6]}\nПродавец: @{name[8]}\nРейтинг продавца: {average[0]}\nКол-во отзывов: {average[1]}"
    builder = MediaGroupBuilder(caption=text)
    for i in a:
        builder.add_photo(media=f'{i}')
    await message.answer_media_group(media=builder.build())

@rt.callback_query(F.data == 'name')
async def edit_name(call: CallbackQuery, state: FSMContext):
    rows = [[buttons[4]]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)

    await call.message.edit_text(text=f'Введите новое название товара:',
                                 reply_markup=markup)
    await state.set_state(edit_product.name)

@rt.callback_query(F.data == 'description')
async def edit_description(call: CallbackQuery, state: FSMContext):
    rows = [[buttons[4]]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)

    await call.message.edit_text(text=f'Введите новое описание товара:',
                                 reply_markup=markup)
    await state.set_state(edit_product.description)

@rt.callback_query(F.data == 'price')
async def edit_price(call: CallbackQuery, state: FSMContext):
    rows = [[buttons[4]]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)

    await call.message.edit_text(text=f'Введите новую цену товара:',
                                 reply_markup=markup)
    await state.set_state(edit_product.price)

@rt.callback_query(F.data == 'locate')
async def edit_locate(call: CallbackQuery, state: FSMContext):
    rows = [[buttons[4]]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)

    await call.message.edit_text(text=f'Введите новое место встречи с покупателем:',
                                 reply_markup=markup)
    await state.set_state(edit_product.locate)

@rt.message(edit_product.name)
async def edit_photo_2(message: Message, state: FSMContext, bot: Bot):
    but = [[types.InlineKeyboardButton(text="Внести изменения", callback_data='edit_yes_text')]]
    markup_2 = InlineKeyboardMarkup(inline_keyboard=but)

    await state.update_data(name=message.text)
    data = await state.get_data()

    await edit_def('offer_name', data['name'], call_data)
    await send_media(message)
    await message.answer(text='Вот так теперь выглядит ваше объявление⬆️', reply_markup=markup_2)
    await state.clear()

@rt.message(edit_product.description)
async def edit_photo_2(message: Message, state: FSMContext, bot: Bot):
    but = [[types.InlineKeyboardButton(text="Внести изменения", callback_data='edit_yes_text')]]
    markup_2 = InlineKeyboardMarkup(inline_keyboard=but)

    await state.update_data(description=message.text)
    data = await state.get_data()

    await edit_def('description', data['description'], call_data)
    await send_media(message)
    await message.answer(text='Вот так теперь выглядит ваше объявление⬆️', reply_markup=markup_2)
    await state.clear()

@rt.message(edit_product.price)
async def edit_photo_2(message: Message, state: FSMContext, bot: Bot):
    but = [[types.InlineKeyboardButton(text="Внести изменения", callback_data='edit_yes_text')]]
    markup_2 = InlineKeyboardMarkup(inline_keyboard=but)

    await state.update_data(price=message.text)
    data = await state.get_data()

    await edit_def('price', data['price'], call_data)
    await send_media(message)
    await message.answer(text='Вот так теперь выглядит ваше объявление⬆️', reply_markup=markup_2)
    await state.clear()

@rt.message(edit_product.locate)
async def edit_photo_2(message: Message, state: FSMContext, bot: Bot):
    but = [[types.InlineKeyboardButton(text="Внести изменения", callback_data='edit_yes_text')]]
    markup_2 = InlineKeyboardMarkup(inline_keyboard=but)

    await state.update_data(locate=message.text)
    data = await state.get_data()

    await edit_def('locate', data['locate'], call_data)
    await send_media(message)
    await message.answer(text='Вот так теперь выглядит ваше объявление⬆️', reply_markup=markup_2)
    await state.clear()
