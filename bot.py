import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

API_TOKEN = "8370996003:AAFhqnl8SoAvQnb1XSY02QbF-3mq05-ptDs"
ADMIN_USERNAME = "@chrvvvv"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Start command
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Ro'yxatdan o'tish", callback_data='register'))
    await message.reply("""
Salom! "Siz mo‘tabarsiz aziz onajon" ko‘rik-tanloviga xush kelibsiz.
Ro‘yxatdan o‘tish uchun quyidagi tugmani bosing.
    """, reply_markup=keyboard)

# Registration handler
@dp.callback_query_handler(lambda c: c.data == 'register')
async def process_register(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, """
Ro‘yxatdan o‘tish uchun quyidagi ma’lumotlarni yuboring:
1. Ism-familiya
2. Yosh (8-18)
3. Manzil (shahar/tuman)
4. Telefon raqam
5. Ijodiy ish haqida qisqacha ma’lumot (video yoki matn)

Ma’lumotlarni shu xabarga javoban ketma-ket yuboring.
    """)

# Message handler for registration data
@dp.message_handler()
async def save_data(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    text = message.text
    
    # Adminga xabar yuborish
    admin_message = f"📥 Yangi ro'yxatdan o'tish:\n\n👤 Foydalanuvchi: @{username}\n🆔 ID: {user_id}\n📝 Ma'lumot: {text}"
    await bot.send_message(chat_id=ADMIN_USERNAME, text=admin_message)
    
    # Foydalanuvchiga javob
    await message.reply("✅ Ma’lumotlaringiz qabul qilindi. Adminlar tez orada siz bilan bog‘lanadi.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
