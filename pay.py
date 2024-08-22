from aiocryptopay import AioCryptoPay, Networks
from aiogram import types, Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery, ReplyKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from aiogram.filters import Command
from aiogram.utils.media_group import MediaGroupBuilder
import sqlite3
import asyncio
from reply import buttons
from hand import offer_def, id_list_pay, forward, average_rating, del_media, edit_def
from inf import CRYPTO, CHANNEL_ID
import pytz
import datetime
from datetime import timedelta
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

@rt_5.callback_query(lambda query: query.data in id_list_pay)
async def pay_offer_menu(call: CallbackQuery, bot: Bot):
    global call_data, call_inf, id_msg_2, id_list_pay
    await call.message.delete()
    id_list_pay.clear()
    call_data = call.data
    call_data = call_data.replace('_pay', '')
    call_inf = call
    id_msg_2 = await forward(call.message, call_data)
    rows = [[InlineKeyboardButton(text='Рассылка объявления', callback_data='dispatch_offer')],
            [InlineKeyboardButton(text='Автопубликация', callback_data='auto_posting')],
            [InlineKeyboardButton(text='Назад⬅️', callback_data='pay')]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await call.message.answer(text='Выберите товар', reply_markup=markup)

@rt_5.callback_query(F.data == 'pay')
async def pay(call: CallbackQuery):
    rows = offer_def(call.message, 'pay')
    if len(rows) == 1:
        row = [[buttons[0]],
               [buttons[4]]]
        markup = InlineKeyboardMarkup(inline_keyboard=row)
        await call.message.edit_text(text='У вас нет опубликованных объявлений', reply_markup=markup)
    else:
        markup = InlineKeyboardMarkup(inline_keyboard=rows)
        await call.message.edit_text(text='ssds', reply_markup=markup)

@rt_5.callback_query(F.data == 'dispatch_offer')
async def dispatch(call: CallbackQuery):
    rows = [[InlineKeyboardButton(text='Оплатить', callback_data='dispatch_pay')],
            [InlineKeyboardButton(text='Назад', callback_data='pay')]]
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
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"SELECT offer_id_channel FROM auto_posting WHERE offer_id_channel = '{call_data}'")
    data = cur.fetchone()
    db.commit()
    db.close()
    if data == None:
        rows = [[InlineKeyboardButton(text='Купить тариф на 7 дней', callback_data='7day')],
                [InlineKeyboardButton(text='Купить тариф на 30 дней', callback_data='30day')],
                [InlineKeyboardButton(text='Назад', callback_data='pay')]]
        markup = InlineKeyboardMarkup(inline_keyboard=rows)
        await call.message.edit_text(text='Описание продукта', reply_markup=markup)
    else:
        rows = [[InlineKeyboardButton(text='Назад', callback_data='pay')]]
        markup = InlineKeyboardMarkup(inline_keyboard=rows)
        db = sqlite3.connect('users.db')
        cur = db.cursor()
        cur.execute(f"SELECT final FROM auto_posting WHERE offer_id_channel = '{call_data}'")
        still_time = cur.fetchone()
        db.commit()
        db.close()
        still_time_2 = still_time[0].split('-')
        still_time = datetime.datetime(int(still_time_2[0]), int(still_time_2[1]), int(still_time_2[2]), tzinfo=tz) - datetime.datetime.now(tz)
        await call.message.edit_text(text=f'Это объявление уже используется в тарифе.\n\nДо конца тарифа {still_time.days + 1} дней ', reply_markup=markup)

@rt_5.callback_query(F.data == '7day')
async def auto_posting(call: CallbackQuery):
    global pay_def
    pay_def = await creat(0.01)
    rows = [[InlineKeyboardButton(text='Оплатить', url=pay_def.bot_invoice_url)],
            [InlineKeyboardButton(text='Проверить оплату', callback_data='chek_auto_pay_7')]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await call.message.edit_text(text=f'Оплата тарифа на 7 дней', reply_markup=markup)

@rt_5.callback_query(F.data == '30day')
async def auto_posting(call: CallbackQuery):
    global pay_def
    pay_def = await creat(0.01)
    rows = [[InlineKeyboardButton(text='Оплатить', url=pay_def.bot_invoice_url)],
            [InlineKeyboardButton(text='Проверить оплату', callback_data='chek_auto_pay_30')]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await call.message.edit_text(text=f'Оплата тарифа на 30 дней', reply_markup=markup)

@rt_5.callback_query(lambda query: query.data in ['chek_auto_pay_7', 'chek_auto_pay_30'])
async def auto_posting(call: CallbackQuery, bot: Bot):
    chek = await creat_2(pay_def, call.message)

    if chek == True:
        if call.data == 'chek_auto_pay_7':
            tarif = 7
        if call.data == 'chek_auto_pay_30':
            tarif = 30
        date = datetime.datetime.strptime(f'{datetime.date.today()}', '%Y-%m-%d')
        new_date = date + timedelta(days=tarif)
        await call.message.edit_text(text='Оплата прошла')
        db = sqlite3.connect('users.db')
        cur = db.cursor()
        cur.execute(f"INSERT INTO auto_posting VALUES ('{call.message.chat.id}', '{call_data}', '{call.message.from_user.username}', '{datetime.date.today()}', '{new_date.strftime('%Y-%m-%d')}')")
        db.commit()
        db.close()
    if chek == False:
        await bot.answer_callback_query(callback_query_id=call.id, text='Оплата не прошла', show_alert=True)