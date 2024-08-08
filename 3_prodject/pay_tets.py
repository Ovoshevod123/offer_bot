from aiocryptopay import AioCryptoPay, Networks
from aiogram import types, Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery, ReplyKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from aiogram.filters import Command
from aiogram.utils.media_group import MediaGroupBuilder

rt_4 = Router()
crypto = AioCryptoPay(token='248639:AARhZfXeXq5xLeP8btjOOo9TSTRwkh7tX4Z', network=Networks.MAIN_NET)

@rt_4.callback_query(F.data == 'pay')
async def pay(call: CallbackQuery):
    global pay
    rows = [[InlineKeyboardButton(text='Проверить', callback_data='chek_pay')]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    pay = await creat()
    await call.message.edit_text(text=f'sdsd\n{pay.bot_invoice_url}', reply_markup=markup)

@rt_4.callback_query(F.data == 'chek_pay')
async def chek_pay(call: CallbackQuery):
    await creat_2(pay)

async def creat():
    invoice = await crypto.create_invoice(asset='USDT', amount=0.1)
    return invoice

async def creat_2(invoice):
    invoices = await crypto.get_invoices(invoice_ids=invoice.invoice_id)
    if invoices.status == 'paid':
        print('yes')
    if invoices.status == 'active':
        print('no')