from aiocryptopay import AioCryptoPay, Networks
from aiogram import types, Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery, ReplyKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from aiogram.filters import Command
from aiogram.utils.media_group import MediaGroupBuilder
import sqlite3
import asyncio
from hand import offer_def, id_list_pay, forward, average_rating, del_media, edit_def
from inf import CRYPTO, CHANNEL_ID
import pytz
import datetime
tz = pytz.timezone("Europe/Samara")

rt_5 = Router()
crypto = AioCryptoPay(token=CRYPTO, network=Networks.MAIN_NET)

async def creat(price):
    invoice = await crypto.create_invoice(asset='USDT', amount=price)
    return invoice

async def creat_2(invoice, message):
    invoices = await crypto.get_invoices(invoice_ids=invoice.invoice_id)
    if invoices.status == 'paid':
        return True
    if invoices.status == 'active':
        return False

async def send_media(message, bot):
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
    text = f"Цена: {name[5]}\n{name[3]}\n{name[4]}\n{name[6]}\n\nПродавец: @{name[8]}\nРейтинг продавца: {average[0]}\nКол-во отзывов: {average[1]}"
    # builder = MediaGroupBuilder(caption=text)
    # for i in a:
    #     builder.add_photo(media=f'{i}')
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

    # await edit_def('offer_id_channel', send_02[0].message_id, call_data)
    await del_media(bot, call_data)
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    # cur.execute(f"DELETE from users_offer WHERE offer_id_channel = {call_data}")
    cur.execute(f"INSERT INTO users_offer VALUES ('{name[0]}', '{send_02[0].message_id}', '{name[2]}', '{name[3]}', '{name[4]}', '{name[5]}', '{name[6]}', '{name[7]}', '{name[8]}')")
    db.commit()
    db.close()

@rt_5.callback_query(lambda query: query.data in id_list_pay)
async def pay_offer_menu(call: CallbackQuery, bot: Bot):
    global call_data, call_inf, id_msg_2, id_list_pay
    await call.message.delete()
    id_list_pay.clear()
    call_data = call.data
    call_data = call_data.replace('_pay', '')
    call_inf = call
    id_msg_2 = await forward(call.message, call_data)
    rows = [[InlineKeyboardButton(text='Рассылка объявления', callback_data='dispatch_offer'), InlineKeyboardButton(text='Автопубликация', callback_data='auto_posting')]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await call.message.answer(text='Выберите товар', reply_markup=markup)

@rt_5.callback_query(F.data == 'pay')
async def pay(call: CallbackQuery):
    rows = offer_def(call.message, 'pay')
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await call.message.edit_text(text='ssds', reply_markup=markup)

@rt_5.callback_query(F.data == 'dispatch_offer')
async def dispatch(call: CallbackQuery):
    rows = [[InlineKeyboardButton(text='Оплатить', callback_data='dispatch_pay'), InlineKeyboardButton(text='Назад', callback_data='pay')]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await call.message.edit_text(text='Описание продукта', reply_markup=markup)

@rt_5.callback_query(F.data == 'dispatch_pay')
async def dispatch(call: CallbackQuery):
    global pay_def
    pay_def = await creat(0.01)
    rows = [[InlineKeyboardButton(text='Оплатить', url=pay_def.bot_invoice_url)],
        [InlineKeyboardButton(text='Проверить оплату', callback_data='chek_dispatch_pay')]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await call.message.edit_text(text=f'sdsd', reply_markup=markup)

@rt_5.callback_query(F.data == 'chek_dispatch_pay')
async def dispatch(call: CallbackQuery, bot: Bot):
    chek = await creat_2(pay_def, call.message)
    if chek == True:
        await call.message.edit_text(text='Оплата прошла успешно')
        db = sqlite3.connect('users.db')
        cur = db.cursor()
        cur.execute("SELECT id FROM users")
        ids = cur.fetchall()
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
        for i in ids[0]:
            await bot.send_media_group(chat_id=i, media=builder.build())
    if chek == False:
        await bot.answer_callback_query(callback_query_id=call.id, text='Оплата не прошла', show_alert=True)

@rt_5.callback_query(F.data == 'auto_posting')
async def auto_posting(call: CallbackQuery):
    rows = [[InlineKeyboardButton(text='Оплатить', callback_data='auto_pay'), InlineKeyboardButton(text='Назад', callback_data='pay')]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await call.message.edit_text(text='Описание продукта', reply_markup=markup)

@rt_5.callback_query(F.data == 'auto_pay')
async def auto_posting(call: CallbackQuery):
    global pay_def
    pay_def = await creat(0.01)
    rows = [[InlineKeyboardButton(text='Оплатить', url=pay_def.bot_invoice_url)],
            [InlineKeyboardButton(text='Проверить оплату', callback_data='chek_auto_pay')]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await call.message.edit_text(text=f'sdsd', reply_markup=markup)

@rt_5.callback_query(F.data == 'chek_auto_pay')
async def auto_posting(call: CallbackQuery, bot: Bot):
    chek = await creat_2(pay_def, call.message)
    if chek == True:
        await call.message.edit_text(text='Оплата прошла')
        while True:
            if int(datetime.datetime.now(tz).time().hour) == 14 and int(datetime.datetime.now(tz).time().minute) == 17:
                await send_media(call.message, bot)
                await asyncio.sleep(70)
            await asyncio.sleep(5)
    if chek == False:
        await bot.answer_callback_query(callback_query_id=call.id, text='Оплата не прошла', show_alert=True)