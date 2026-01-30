import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Tokens
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8370996003:AAFhqnl8SoAvQnb1XSY02QbF-3mq05-ptDs")
ADMIN = os.getenv("ADMIN_USERNAME", "@chrvvvv")

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    btn = InlineKeyboardButton(text="Ro'yxatdan o'tish", callback_data="register")
    kb = InlineKeyboardMarkup(inline_keyboard=[[btn]])
    
    text = """Salom! Tanlovga xush kelibsiz.
Ro'yxatdan o'tish uchun tugmani bosing."""
    
    await message.answer(text, reply_markup=kb)

@dp.callback_query(lambda c: c.data == "register")
async def register_callback(callback: types.CallbackQuery):
    await callback.answer()
    text = """Ma'lumotlarni yuboring:
1. Ism-familiya
2. Yosh
3. Manzil
4. Telefon
5. Ish haqida ma'lumot"""
    
    await callback.message.answer(text)

@dp.message()
async def all_messages(message: types.Message):
    user_info = f"Foydalanuvchi: @{message.from_user.username}\nID: {message.from_user.id}\nXabar: {message.text}"
    
    # Admin ga yuborish
    await bot.send_message(chat_id=ADMIN, text=f"📥 Yangi ariza:\n{user_info}")
    
    # Foydalanuvchiga javob
    await message.answer("✅ Qabul qilindi. Admin bog'lanadi.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import asyncio
    asyncio.run(main())
