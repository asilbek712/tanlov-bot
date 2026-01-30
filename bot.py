import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import F
from aiogram.client.default import DefaultBotProperties

# YANGI TOKEN
TOKEN = "8483323640:AAF6ti4BpL3npCITChDPYoKP734VdjCIwug"
ADMIN = "@chrvvvv"

# Bot yaratish
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# /start
@dp.message(Command("start"))
async def start_cmd(message: Message):
    button = InlineKeyboardButton(text="Ro'yxatdan o'tish", callback_data="register")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])
    
    text = """Salom! "Siz mo'tabarsiz aziz onajon" tanloviga xush kelibsiz.
Ro'yxatdan o'tish uchun tugmani bosing."""
    
    await message.answer(text, reply_markup=keyboard)

# Ro'yxatdan o'tish
@dp.callback_query(F.data == "register")
async def register_cmd(callback: CallbackQuery):
    await callback.answer()
    
    text = """Quyidagi ma'lumotlarni ketma-ket yuboring:

1. Ism-familiya
2. Yosh (8-18)
3. Manzil (shahar/tuman)
4. Telefon raqam
5. Ijodiy ish haqida qisqacha ma'lumot"""
    
    await callback.message.answer(text)

# Barcha xabarlar
@dp.message()
async def all_msgs(message: Message):
    user = message.from_user
    msg_text = message.text or "Fayl yuborildi"
    username = user.username or "Noma'lum"
    
    # Admin ga yuborish
    admin_msg = f"📥 Yangi ro'yxatdan o'tish:\n\n👤 Foydalanuvchi: @{username}\n🆔 ID: {user.id}\n📝 Xabar: {msg_text}"
    
    try:
        await bot.send_message(chat_id=ADMIN, text=admin_msg)
    except Exception as e:
        logging.error(f"Admin ga yuborishda xato: {e}")
    
    # Foydalanuvchiga javob
    await message.answer("✅ Ma'lumotlaringiz qabul qilindi. Adminlar tez orada bog'lanadi.")

# Asosiy funksiya
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
