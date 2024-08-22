from aiogram.types import Message, KeyboardButton, ReplyKeyboardRemove, \
    KeyboardButtonPollType, InlineKeyboardButton, InlineKeyboardMarkup, \
    CallbackQuery
from aiogram import F, Router
import sqlite3

rt_2 = Router()

new = InlineKeyboardButton(text='Новое оъявление🆕', callback_data='new')
my_off = InlineKeyboardButton(text='Мои объявления📜', callback_data='my_off')
back = InlineKeyboardButton(text='Назад⬅️', callback_data='back')
new_2 = InlineKeyboardButton(text='Заполнить объявление заново🔄', callback_data='new')
good = InlineKeyboardButton(text='Опубликовать✅', callback_data='good')
pay = InlineKeyboardButton(text='Платные тарифы💰', callback_data='pay')
fb = InlineKeyboardButton(text='Меню отзывов💬', callback_data='fb_menu')
account = InlineKeyboardButton(text='Личный кабинет', callback_data='account')

delete_final = InlineKeyboardButton(text='Удалить🗑️', callback_data='dell')
edit = InlineKeyboardButton(text='Редактировать✏️', callback_data='edit')
back_edit = InlineKeyboardButton(text='Назад⬅️', callback_data='back_2')

edit_photo = InlineKeyboardButton(text='Изменить фото', callback_data='photo')
edit_name = InlineKeyboardButton(text='Изменить название', callback_data='name')
edit_description = InlineKeyboardButton(text='Изменить описание', callback_data='description')
edit_price = InlineKeyboardButton(text='Изменить цену', callback_data='price')
edit_locate = InlineKeyboardButton(text='Изменить место встречи', callback_data='locate')
edit_back = InlineKeyboardButton(text='Назад⬅️', callback_data='no')

buttons = [new, account, new_2, good, back, pay, fb, my_off]

edit_but = [delete_final, edit, back_edit]

buttons_edit = [edit_photo, edit_price, edit_name, edit_description, edit_locate, edit_back]

def but_del(send_01, from_var):
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"SELECT offer_name FROM users_offer WHERE id = '{send_01.chat.id}'")
    name = cur.fetchall()
    cur.execute(f"SELECT offer_id_channel FROM users_offer WHERE id = '{send_01.chat.id}'")
    id_channel = cur.fetchall()
    data = dict(zip(id_channel, name))
    butt_del = []
    a = []
    for i in data:
        if i != None:
            name_i = InlineKeyboardButton(text=f'{data[i][0]}', callback_data=f'{i[0]}_{from_var}')
            butt_del.append(name_i)
        else:
            break
    for i in range(0, len(butt_del)-1, 2):
        b = [butt_del[i], butt_del[i+1]]
        a.append(b)
    if len(butt_del) % 2 == 1:
        b = [butt_del[-1]]
        c = [buttons[4]]
        a.append(b)
        a.append(c)
    else:
        c = [buttons[4]]
        a.append(c)

    db.commit()
    db.close()
    return a, data