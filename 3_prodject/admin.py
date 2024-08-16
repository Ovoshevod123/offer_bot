import asyncio
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery, ReplyKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
import datetime
import pytz
import sqlite3
from hand import average_rating, del_media
from inf import ADMIN_LIST, CHANNEL_ID

rt_4 = Router()

tz = pytz.timezone("Europe/Samara")

@rt_4.message(Command('admin'))
async def chek_admin(message: Message):
    rows = [[InlineKeyboardButton(text='Запуск авто-постинга', callback_data='ap')]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    if message.chat.id == ADMIN_LIST:
        await message.answer(text='Добро пожаловать', reply_markup=markup)

@rt_4.callback_query(F.data == 'ap')
async def auto_posting(call: CallbackQuery, bot: Bot):
    while True:
        if int(datetime.datetime.now(tz).time().hour) == 00 and int(datetime.datetime.now(tz).time().minute) == 28:
            db = sqlite3.connect('users.db')
            cur = db.cursor()
            cur.execute(f"SELECT offer_id_channel, final FROM auto_posting")
            ids = cur.fetchall()
            db.commit()
            db.close()
            for i in ids:
                still_time = i[1].split('-')
                still_time = datetime.datetime(int(still_time[0]), int(still_time[1]), int(still_time[2]), tzinfo=tz) - datetime.datetime.now(tz)
                print(i, still_time.days + 1)
                if still_time.days + 1 == -1:
                    db = sqlite3.connect('users.db')
                    cur = db.cursor()
                    print(ids[0][0])
                    cur.execute(f"DELETE from auto_posting WHERE offer_id_channel = {ids[0][0]}")
                    db.commit()
                    db.close()
                else:
                    await send_media(bot, i[0])
            await asyncio.sleep(82800)
        await asyncio.sleep(30)

async def send_media(bot, offer_id):
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"SELECT * FROM users_offer WHERE offer_id_channel = '{offer_id}'")
    name = cur.fetchall()
    db.commit()
    db.close()
    name = name[0]
    a = name[2]
    a = a.split('|')
    a.pop(0)
    average = await average_rating(name[8])
    text = f"Цена: {name[5]}\n{name[3]}\n{name[4]}\n{name[6]}\n\nПродавец: @{name[8]}\nРейтинг продавца: {average[0]}\nКол-во отзывов: {average[1]}"
    col = len(a)
    if col > 1:
        media = [
            types.InputMediaPhoto(media=a[0], caption=text),
            *[types.InputMediaPhoto(media=photo_id) for photo_id in a[1:]]
        ]
    else:
        media = [types.InputMediaPhoto(media=a[0], caption=text)]
    send_02 = await bot.send_media_group(chat_id=CHANNEL_ID, media=media)
    await bot.edit_message_caption(chat_id=CHANNEL_ID, message_id=send_02[0].message_id, caption=text + f'\nid сообщения: {send_02[0].message_id}')

    await del_media(bot, offer_id)
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"SELECT * FROM auto_posting WHERE offer_id_channel = '{offer_id}'")
    name_2 = cur.fetchall()
    name_2 = name_2[0]
    cur.execute(f"DELETE from users_offer WHERE offer_id_channel = {offer_id}")
    cur.execute(f"DELETE from auto_posting WHERE offer_id_channel = {offer_id}")
    cur.execute(f"INSERT INTO users_offer VALUES ('{name[0]}', '{send_02[0].message_id}', '{name[2]}', '{name[3]}', '{name[4]}', '{name[5]}', '{name[6]}', '{name[7]}', '{name[8]}')")
    cur.execute(f"INSERT INTO auto_posting VALUES ('{name_2[0]}', '{send_02[0].message_id}', '{name_2[2]}', '{name_2[3]}', '{name_2[4]}')")
    db.commit()
    db.close()