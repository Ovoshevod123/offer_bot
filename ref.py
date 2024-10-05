from aiogram import types, Router, F, Bot
from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery, ReplyKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from aiogram.filters import Command
import sqlite3
import time
import asyncio
from hand import send_01

rt_6 = Router()

@rt_6.callback_query(F.data == 'ref')
async def ref_1(call: CallbackQuery):
    rows = [[(InlineKeyboardButton(text='‹ Назад', callback_data='account'))]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await call.message.edit_text(text='Ваша реферальная ссылка:\n'
                                      f'https://t.me/VBaraholka_bot/?start={call.message.chat.id}', reply_markup=markup)