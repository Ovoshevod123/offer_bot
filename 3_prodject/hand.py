from aiogram import types, Router, F, Bot, filters
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery, ReplyKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, StateFilter
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.enums import ParseMode
import sqlite3
import time
from reply import buttons, but_del, edit_but
from inf import CHANNEL_ID

rt = Router()

photo = []
id_list = []
class new_product(StatesGroup):
    photo = State()
    name = State()
    description = State()
    price = State()
    locate = State()

@rt.message(Command('start'))
async def start(message: Message):
    global send_01
    rows = [[buttons[1]],
            [buttons[0]]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await message.answer(text='Здравсвуйте', reply_markup=markup)
    send_01 = message

@rt.callback_query(F.data == 'back')
async def back(call: CallbackQuery, bot: Bot):
    rows = [[buttons[1]],
            [buttons[0]]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await call.message.edit_text(text='Здравсвуйте', reply_markup=markup)

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
    text = f"Цена: {data['price']}\n{data['name']}\n{data['description']}\n{data['locate']}\nПродавец: @{message.from_user.username}\nРейтинг продавца: 4,89/5"
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
    global send_01
    rows = [[buttons[0], buttons[1]]]
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

    photo.clear()
    db = sqlite3.connect('users.db')
    cur = db.cursor()

    cur.execute(f"INSERT INTO users VALUES ('{send_01.from_user.id}', '{send_01.from_user.username}', '{send_01.from_user.full_name}', {send[0].message_id}, {send_02[0].message_id}, '{name_ofer}')")

    db.commit()
    db.close()

    db = sqlite3.connect('users_offers.db')
    cur = db.cursor()

    cur.execute(f"""INSERT INTO users VALUES ('{send_01.chat.id}', '{send_02[0].message_id}', '{data_state['photo']}', '{data_state['name']}', '{data_state['description']}', '{data_state['price']}', '{data_state['locate']}')""")

    db.commit()
    db.close()

    await callback.message.edit_text(text='Теперь твое объявление опубликованно <a href="https://t.me/jxddkcj">здесь</a>.', parse_mode='HTML', reply_markup=markup)


def offer_def():
    global id_list, deff
    id_list = []
    deff = but_del(send_01=send_01)
    for i in deff[1].keys():
        id_list.append(f'{i[0]}')
    row = deff[0]
    return row

@rt.callback_query(F.data == 'delete')
async def delete_0(call: CallbackQuery):
    rows = offer_def()
    rows_2 = [[buttons[0]],
              [buttons[4]]]
    if len(rows) == 1:
        markup = InlineKeyboardMarkup(inline_keyboard=rows_2)
        await call.message.edit_text(text='У вас нет активных объявлений(\n\nХотите создать новое объявление?', reply_markup=markup)
    else:
        markup = InlineKeyboardMarkup(inline_keyboard=rows)
        await call.message.edit_text(text='Выберите товар:', reply_markup=markup)

@rt.callback_query(F.data == 'back_2')
async def back_edit(call: CallbackQuery):
    # rows = deff[0]
    # markup = InlineKeyboardMarkup(inline_keyboard=rows)
    # await call.message.edit_text(text='Выберите товар:', reply_markup=markup)
    await delete_0(call)

@rt.callback_query(lambda query: query.data in id_list)
async def delete_1(call: CallbackQuery, bot: Bot):
    global call_data
    call_data = call.data
    rows = [[edit_but[0], edit_but[1]],
            [edit_but[2]]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await bot.forward_message(call.message.chat.id, CHANNEL_ID, call_data)
    await call.message.answer(text='Это ваше объявление⬆️\n\nЧто хотите сделать?', reply_markup=markup)

@rt.callback_query(F.data == 'dell')
async def back_edit(call: CallbackQuery):
    rows = [[InlineKeyboardButton(text='Да', callback_data='yes'), InlineKeyboardButton(text='Нет', callback_data='no')]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await call.message.edit_text(text='Вы уверены что хотите удалить объявление?', reply_markup=markup)

@rt.callback_query(F.data == 'yes')
async def back_edit(call: CallbackQuery, bot: Bot):
    db = sqlite3.connect('users.db')
    cur = db.cursor()

    cur.execute(f"DELETE from users where offer_id_channel = {call_data}")
    await bot.delete_message(chat_id=CHANNEL_ID, message_id=call_data)
    await call.message.edit_text(text='Объявление удалено.')
    time.sleep(1.5)

    db.commit()
    db.close()

    await delete_0(call)

@rt.callback_query(F.data == 'no')
async def back_edit(call: CallbackQuery):
    rows = [[edit_but[0], edit_but[1]],
            [edit_but[2]]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await call.message.edit_text(text='Это ваше объявление⬆️\n\nЧто хотите сделать?', reply_markup=markup)

@rt.callback_query(F.data == 'edit')
async def edit_0(call: CallbackQuery):
    pass