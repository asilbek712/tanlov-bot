import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram import F
from aiogram.client.default import DefaultBotProperties

# TOKEN
TOKEN = "8483323640:AAF6ti4BpL3npCITChDPYoKP734VdjCIwug"
ADMIN = "@chrvvvv"

# Bot yaratish
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# /start
@dp.message(Command("start"))
async def start_cmd(message: Message):
    # Faylni yuklash
    doc_file = FSInputFile("14-fevral Zahriddin Muxammad Bobur.docx")
    
    # Havola tugmasi
    button1 = InlineKeyboardButton(text="📄 Tanlov nizomini yuklab olish", callback_data="download_doc")
    button2 = InlineKeyboardButton(text="📝 Ro'yxatdan o'tish", callback_data="register")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button1], [button2]])
    
    start_text = """📣 🔤🔤🔤🔤🔤🔤📣

"Bobur vorislari" viloyat onlayn videoroliklar tanlovi o‘tkaziladi... 

📍Qashqadaryo viloyat tuman, shahar "Kelajak" markazlari to‘garak aʼzolari o‘rtasida Zahiriddin Muhammad Bobur tavalludining 543 yilligi munosabati bilan, uning hayoti va ijodi yuzasidan onlayn videoroliklar tanlovi tashkil etilmoqda. 

⬇️Mazkur tanlov: 
◾️viloyat tuman, shahar "Kelajak" markazlari to‘garak aʼzolari; 
◾️umumiy o‘rta taʼlim maktabi o‘quvchilari o‘rtasida o‘tkaziladi. 

📌Onlayn videorolik tanlov nizomi bilan batafsil quyidagi havola tanishing!

👏Tanlov g‘oliblari viloyat "Kelajak" markazi tomonidan maxsus diplom va esdalik sovg‘alari bilan taqdirlanadi.

🗓Tanlov:
😐2026-yil 4-fevral kunidan 12  fevral kuniga qadar "Bobur vorislari" sarlavhasi ostida @tanlov2026_bot telegram botida o‘tkaziladi.
😐Ijodiy ishlarni @chrvvvv telegram manziliga yuborishingiz so‘raladi.

🔘Tanlovning asosiy maqsadi:
✅ To‘garak aʼzolari hamda o‘quvchi yoshlarning shoh va shoir Bobur hayoti va ijodiga qiziqishini oshirish, ularni maʼnaviy maʼrifiy ruhda tarbiyalash, nutq madaniyati va axborot texnologiyalardan foydalanish ko‘nikmalarini rivojlantirishdan iborat. 

Maʼlumot uchun: 
Qatnashchilar videorolik tayyorlash jarayonida Bobur ruboiylari, g‘azallaridan birini ifodali o‘qib berishi yoki shoh va shoir haqida maʼruza tayyorlashi, olinadigan video esa 2 daqiqa, 50 mb dan oshmasligi lozim. 

Qashqadaryo viloyat "Kelajak" markazi 
🌍🌍🌍🌍🌍🌍

Bizni kuzating
📱Telegram  📱Facebook
📱Instagram"""
    
    await message.answer(start_text, reply_markup=keyboard)

# Faylni yuklash uchun callback
@dp.callback_query(F.data == "download_doc")
async def download_doc_cmd(callback: CallbackQuery):
    await callback.answer()
    doc_file = FSInputFile("14-fevral Zahriddin Muxammad Bobur.docx")
    await callback.message.answer_document(document=doc_file, caption="📄 Tanlov nizomi")

# Ro'yxatdan o'tish
@dp.callback_query(F.data == "register")
async def register_cmd(callback: CallbackQuery):
    await callback.answer()
    
    text = """Quyidagi ma'lumotlarni ketma ket yuboring:

1. Ism familiya
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
    
    # Admin ga yuborish (faqat admin mavjud bo'lsa)
    admin_msg = f"📥 Yangi ro'yxatdan o'tish:\n\n👤 Foydalanuvchi: @{username}\n🆔 ID: {user.id}\n📝 Xabar: {msg_text}"
    
    try:
        await bot.send_message(chat_id=ADMIN, text=admin_msg)
    except Exception as e:
        logging.error(f"Admin ga yuborishda xato: {e}")
        # Xato bo'lsa ham foydalanuvchiga javob berish
        pass
    
    # Foydalanuvchiga javob
    await message.answer("✅ Ma'lumotlaringiz qabul qilindi. Adminlar tez orada bog'lanadi.")

# Asosiy funksiya
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
