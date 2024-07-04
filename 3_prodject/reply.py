from aiogram.types import Message, KeyboardButton, ReplyKeyboardRemove, \
    KeyboardButtonPollType, InlineKeyboardButton, InlineKeyboardMarkup, \
    CallbackQuery
from aiogram import F, Router
import sqlite3

rt_2 = Router()

new = InlineKeyboardButton(text='Новое оъявление', callback_data='new')
delete = InlineKeyboardButton(text='Мои объявления', callback_data='delete')
back = InlineKeyboardButton(text='Назад', callback_data='back')
new_2 = InlineKeyboardButton(text='Заполнить объявление заново', callback_data='new')
good = InlineKeyboardButton(text='Все верно! Опубликовать', callback_data='good')

delete_final = InlineKeyboardButton(text='Удалить его', callback_data='dell')
edit = InlineKeyboardButton(text='Отредактировать его', callback_data='edit')
back_edit = InlineKeyboardButton(text='Назад', callback_data='back_2')

buttons = [new, delete, new_2, good, back]

edit_but = [delete_final, edit, back_edit]

def but_del(send_01):
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"SELECT name_offer FROM users WHERE id = '{send_01.from_user.id}'")
    name = cur.fetchall()
    cur.execute(f"SELECT offer_id_bot FROM users WHERE id = '{send_01.from_user.id}'")
    id_bot = cur.fetchall()
    cur.execute(f"SELECT offer_id_channel FROM users WHERE id = '{send_01.from_user.id}'")
    id_channel = cur.fetchall()
    data = dict(zip(id_channel, name))
    butt_del = []
    a = []
    for i in data:
        if i != None:
            name_i = InlineKeyboardButton(text=f'{data[i][0]}', callback_data=f'{i[0]}')
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