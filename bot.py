import os
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import F

# Environment variables
API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8370996003:AAFhqnl8SoAvQnb1XSY02QbF-3mq05-ptDs")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "@chrvvvv")

# Bot va Dispatcher
bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Start command
@dp.message(Command("start"))
async def cmd_start(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Ro'yxatdan o'tish", callback_data='register')]
    ])
    await message.answer("""
Salom! "Siz mo‘tabarsiz aziz onajon" ko‘rik-tanloviga xush kelibsiz.
Ro‘yxatdan o‘tish uchun quyidagi tugmani bosing.
    """, reply_markup=keyboard)

# Registration callback
@dp.callback_query(F.data == "register")
async def process_register(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("""
Ro‘yxatdan o‘tish uchun quyidagi ma’lumotlarni yuboring:
1. Ism-familiya
2. Yosh (8-18)
3. Manzil (shahar/tuman)
4. Telefon raqam
5. Ijodiy ish haqida qisqacha ma’lumot (video yoki matn)

Ma’lumotlarni shu xabarga javoban ketma-ket yuboring.
    """)

# All messages handler
@dp.message()
async def save_data(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Noma'lum"
    text = message.text or "Fayl yuborildi"
    
    # Send to admin
    admin_message = f"📥 Yangi ro'yxatdan o'tish:\n\n👤 Foydalanuvchi: @{username}\n🆔 ID: {user_id}\n📝 Ma'lumot: {text}"
    try:
        await bot.send_message(chat_id=ADMIN_USERNAME, text=admin_message)
    except Exception as e:
        logging.error(f"Admin ga xabar yuborishda xato: {e}")
    
    # Reply to user
    await message.answer("✅ Ma'lumotlaringiz qabul qilindi. Adminlar tez orada siz bilan bog'lanadi.")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
