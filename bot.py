import os
import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import F
from aiogram.client.default import DefaultBotProperties

# Tokenni o'qish
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8370996003:AAFhqn18SoAvQnb1XSY02QbF-3mq05-ptDs")
ADMIN = os.getenv("ADMIN_USERNAME", "@chrvvvv")

# Botni ishga tushirish - YANGI USUL
bot = Bot(
    token=TOKEN, 
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# /start buyrug'i
@dp.message(Command("start"))
async def start_handler(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Ro'yxatdan o'tish", callback_data="register")]
        ]
    )
    
    text = "Salom! \"Siz mo'tabarsiz aziz onajon\" tanloviga xush kelibsiz.\nRo'yxatdan o'tish uchun quyidagi tugmani bosing."
    
    await message.answer(text, reply_markup=keyboard)

# Ro'yxatdan o'tish tugmasi bosilganda
@dp.callback_query(F.data == "register")
async def register_handler(callback: CallbackQuery):
    await callback.answer()
    
    text = "Quyidagi ma'lumotlarni ketma-ket yuboring:\n\n1. Ism-familiya\n2. Yosh (8-18)\n3. Manzil (shahar/tuman)\n4. Telefon raqam\n5. Ijodiy ish haqida qisqacha ma'lumot"
    
    await callback.message.answer(text)

# Barcha xabarlarni qayd qilish
@dp.message()
async def all_messages(message: Message):
    user = message.from_user
    user_info = f"📥 Yangi xabar:\n\n👤 Foydalanuvchi: @{user.username or 'Noma\\'lum'}\n🆔 ID: {user.id}\n📝 Xabar: {message.text or 'Fayl yuborildi'}"
    
    # Admin ga yuborish
    try:
        await bot.send_message(chat_id=ADMIN, text=user_info)
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
