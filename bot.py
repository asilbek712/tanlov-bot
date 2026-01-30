import asyncio
import logging
import os
import json
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

# TOKEN
TOKEN = "8483323640:AAF6ti4BpL3npCITChDPYoKP734VdjCIwug"
ADMIN_CHAT_ID = 7548105589  # @chrvvvv ID raqami
ADMIN_USERNAME = "chrvvvv"  # @chrvvvv username

# Bot yaratish
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# FSM holatlari
class Registration(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_location = State()
    waiting_for_phone = State()
    waiting_for_description = State()

# Fayllar ro'yxatlari
IMAGE_FILES = [
    "bobur_poster.jpg",
    "bobur_poster.png",
    "poster.jpg",
    "poster.png",
    "tanlov_rasmi.jpg",
    "tanlov_rasmi.png",
    "rasm.jpg",
    "rasm.png"
]

DOC_FILES = [
    "bobur_nizomi.docx",
    "tanlov_nizomi.docx", 
    "14-fevral Zahriddin Muxammad Bobur.docx"
]

PDF_FILES = [
    "bobur_nizomi.pdf",
    "tanlov_nizom.pdf",
    "nizom.pdf"
]

# Fayl mavjudligini tekshirish
def check_file_exists(file_list):
    for file_name in file_list:
        if os.path.exists(file_name):
            return file_name
    return None

# Admin ma'lumotlarini saqlash
def save_admin_data():
    data = {
        "admin_chat_id": ADMIN_CHAT_ID,
        "admin_username": ADMIN_USERNAME,
        "last_updated": datetime.now().isoformat()
    }
    with open("admin_config.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Faylni yuklash funksiyasi
async def send_file_safe(chat_id, file_path, caption, file_type="document"):
    try:
        if not os.path.exists(file_path):
            return False, "Fayl topilmadi"
        
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            return False, "Fayl bo'sh"
        
        file_obj = FSInputFile(file_path)
        
        if file_type == "photo":
            await bot.send_photo(chat_id=chat_id, photo=file_obj, caption=caption)
        else:
            await bot.send_document(chat_id=chat_id, document=file_obj, caption=caption)
            
        return True, "Muvaffaqiyatli yuborildi"
    except Exception as e:
        logging.error(f"Fayl yuklashda xato: {e}")
        return False, f"Xatolik: {str(e)}"

# Start xabari matni
START_TEXT = """📣 "BOBUR VORISLARI" VILOYAT ONLAYN VIDEOROLIKLAR TANLOVI

"Bobur vorislari" viloyat onlayn videoroliklar tanlovi o‘tkaziladi...

📍 Qashqadaryo viloyat tuman, shahar "Kelajak" markazlari to‘garak aʼzolari o‘rtasida Zahiriddin Muhammad Bobur tavalludining 543 yilligi munosabati bilan, uning hayoti va ijodi yuzasidan onlayn videoroliklar tanlovi tashkil etilmoqda.

🎯 **Maqsad:** Yosh avlodni ma'naviy tarbiyalash, ijodiy qobiliyatlarini rivojlantirish.

📅 **Sana:** 2026-yil 4-12 fevral

👥 **Qatnashuvchilar:** 8-18 yosh

📌 **Ijodiy ish shartlari:**
• Bobur ruboiylari yoki g'azallarini ifodali o'qish
• Yoki Bobur haqida ma'ruza tayyorlash
• Video: 2 daqiqa, 50 MB dan oshmasligi
• O'zbek tilida bo'lishi

🏆 **G'oliblar:** Diplom va sovg'alar bilan taqdirlanadi

📬 **Ijodiy ishlarni yuborish:** @chrvvvv

ℹ️ **Batafsil ma'lumot:** Quyidagi tugmalar orqali"""

# /start - asosiy buyruq
@dp.message(Command("start"))
async def start_cmd(message: Message):
    user = message.from_user
    
    # Admin kirganda log qilish
    if user.id == ADMIN_CHAT_ID:
        logging.info(f"🔥 ADMIN KIRDI: @{user.username} (ID: {user.id})")
    
    # Rasm mavjudligini tekshirish
    image_file = check_file_exists(IMAGE_FILES)
    
    # Tugmalar
    buttons = []
    
    # Nizom fayllari tugmalari
    doc_file = check_file_exists(DOC_FILES)
    pdf_file = check_file_exists(PDF_FILES)
    
    if doc_file:
        buttons.append([InlineKeyboardButton(text="📄 Tanlov nizomi (DOCX)", callback_data="download_doc")])
    
    if pdf_file:
        buttons.append([InlineKeyboardButton(text="📄 Tanlov nizomi (PDF)", callback_data="download_pdf")])
    
    # Ro'yxatdan o'tish
    buttons.append([InlineKeyboardButton(text="📝 Ro'yxatdan o'tish", callback_data="start_registration")])
    
    # Admin bilan bog'lanish
    buttons.append([InlineKeyboardButton(text="👤 Admin bilan bog'lanish", url=f"https://t.me/{ADMIN_USERNAME}")])
    
    # ID ni ko'rish (faqat admin uchun)
    if user.id == ADMIN_CHAT_ID:
        buttons.append([InlineKeyboardButton(text="🆔 ID ni ko'rish", callback_data="show_id")])
        buttons.append([InlineKeyboardButton(text="📊 Statistika", callback_data="show_stats")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    # Rasm mavjud bo'lsa, rasm bilan yuborish
    if image_file:
        success, msg = await send_file_safe(
            message.chat.id, 
            image_file, 
            caption=START_TEXT,
            file_type="photo"
        )
        
        if not success:
            await message.answer(START_TEXT, reply_markup=keyboard)
    else:
        await message.answer(START_TEXT, reply_markup=keyboard)

# /myid - ID ni ko'rish
@dp.message(Command("myid"))
async def myid_cmd(message: Message):
    user = message.from_user
    response = f"""🆔 **Sizning ma'lumotlaringiz:**
ID: `{user.id}`
Username: @{user.username or 'Yo\'q'}
Ism: {user.first_name or ''}
Familiya: {user.last_name or ''}"""
    
    await message.answer(response)
    
    # Admin uchun qo'shimcha ma'lumot
    if user.id == ADMIN_CHAT_ID:
        await message.answer("✅ **Siz adminsiz!** Barcha ro'yxatdan o'tishlar sizga yuboriladi.")

# Admin ID ni ko'rish
@dp.callback_query(F.data == "show_id")
async def show_id_cmd(callback: CallbackQuery):
    await callback.answer()
    user = callback.from_user
    if user.id == ADMIN_CHAT_ID:
        text = f"""🔐 **Admin ma'lumotlari:**
Admin ID: `{ADMIN_CHAT_ID}`
Admin username: @{ADMIN_USERNAME}
Sizning ID: `{user.id}`"""
        await callback.message.answer(text)

# Statistika ko'rsatish (admin uchun)
@dp.callback_query(F.data == "show_stats")
async def show_stats_cmd(callback: CallbackQuery):
    await callback.answer()
    user = callback.from_user
    
    if user.id == ADMIN_CHAT_ID:
        # Fayllarni tekshirish
        doc_file = check_file_exists(DOC_FILES)
        pdf_file = check_file_exists(PDF_FILES)
        image_file = check_file_exists(IMAGE_FILES)
        
        stats_text = """📊 **Bot statistika:**
        
📁 **Fayllar holati:**
"""
        if doc_file:
            doc_size = os.path.getsize(doc_file) / 1024
            stats_text += f"✅ DOCX: {doc_file} ({doc_size:.1f} KB)\n"
        else:
            stats_text += "❌ DOCX fayl topilmadi\n"
            
        if pdf_file:
            pdf_size = os.path.getsize(pdf_file) / 1024
            stats_text += f"✅ PDF: {pdf_file} ({pdf_size:.1f} KB)\n"
        else:
            stats_text += "❌ PDF fayl topilmadi\n"
            
        if image_file:
            img_size = os.path.getsize(image_file) / 1024
            stats_text += f"✅ Rasm: {image_file} ({img_size:.1f} KB)\n"
        else:
            stats_text += "❌ Rasm topilmadi\n"
            
        stats_text += f"\n👤 **Admin:** @{ADMIN_USERNAME}"
        
        await callback.message.answer(stats_text)

# DOCX faylni yuklash
@dp.callback_query(F.data == "download_doc")
async def download_doc_cmd(callback: CallbackQuery):
    await callback.answer("📥 Yuklanmoqda...")
    
    doc_file = check_file_exists(DOC_FILES)
    
    if doc_file:
        success, msg = await send_file_safe(
            callback.message.chat.id,
            doc_file,
            caption="📄 **Tanlov nizomi**\nFaylni yuklab oling va o'qing.",
            file_type="document"
        )
        
        if not success:
            await callback.message.answer(f"❌ {msg}\n\n👤 Admin bilan bog'laning: @{ADMIN_USERNAME}")
    else:
        await callback.message.answer(
            f"❌ Nizom fayli topilmadi.\n\n"
            f"👤 Admin bilan bog'laning: @{ADMIN_USERNAME}"
        )

# PDF faylni yuklash
@dp.callback_query(F.data == "download_pdf")
async def download_pdf_cmd(callback: CallbackQuery):
    await callback.answer("📥 Yuklanmoqda...")
    
    pdf_file = check_file_exists(PDF_FILES)
    
    if pdf_file:
        success, msg = await send_file_safe(
            callback.message.chat.id,
            pdf_file,
            caption="📄 **Tanlov nizomi (PDF)**\nFaylni yuklab oling va o'qing.",
            file_type="document"
        )
        
        if not success:
            await callback.message.answer(f"❌ {msg}\n\n👤 Admin bilan bog'laning: @{ADMIN_USERNAME}")
    else:
        await callback.message.answer(
            f"❌ PDF fayli topilmadi.\n\n"
            f"👤 Admin bilan bog'laning: @{ADMIN_USERNAME}"
        )

# Ro'yxatdan o'tishni boshlash
@dp.callback_query(F.data == "start_registration")
async def start_registration_cmd(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Registration.waiting_for_name)
    
    text = """🎯 **Ro'yxatdan o'tish**

Quyidagi ma'lumotlarni ketma-ket yuboring:

1️⃣ **Ism va familiyangizni** yuboring.
(Misol: *Alisher Navoiy*)"""
    
    await callback.message.answer(text)

# Ism qabul qilish
@dp.message(Registration.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip()
    
    if len(name) < 3:
        await message.answer("❌ Ism va familiya kamida 3 ta belgidan iborat bo'lishi kerak. Qaytadan kiriting:")
        return
    
    # Ismda faqat harf va probel bo'lishi kerak
    if not all(c.isalpha() or c.isspace() for c in name):
        await message.answer("❌ Ism va familiya faqat harflardan iborat bo'lishi kerak. Qaytadan kiriting:")
        return
    
    await state.update_data(full_name=name)
    await state.set_state(Registration.waiting_for_age)
    
    await message.answer(f"""✅ *{name}* qabul qilindi.

2️⃣ **Yoshingizni** yuboring (8-18 yosh oralig'ida).
(Misol: *15*)""")

# Yosh qabul qilish
@dp.message(Registration.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
    try:
        age = int(message.text.strip())
        if not (8 <= age <= 18):
            await message.answer("❌ Yosh 8 dan 18 gacha bo'lishi kerak. Qaytadan kiriting:")
            return
    except ValueError:
        await message.answer("❌ Yosh raqam bo'lishi kerak. Qaytadan kiriting:")
        return
    
    await state.update_data(age=age)
    await state.set_state(Registration.waiting_for_location)
    
    await message.answer(f"""✅ *{age}* yosh qabul qilindi.

3️⃣ **Manzilingizni** yuboring (shahar/tuman).
(Misol: *Qarshi shahri*)""")

# Manzil qabul qilish
@dp.message(Registration.waiting_for_location)
async def process_location(message: Message, state: FSMContext):
    location = message.text.strip()
    
    if len(location) < 3:
        await message.answer("❌ Manzil kamida 3 ta belgidan iborat bo'lishi kerak. Qaytadan kiriting:")
        return
    
    await state.update_data(location=location)
    await state.set_state(Registration.waiting_for_phone)
    
    await message.answer(f"""✅ *{location}* manzili qabul qilindi.

4️⃣ **Telefon raqamingizni** yuboring.
(Misol: *+998901234567* yoki *901234567*)""")

# Telefon qabul qilish
@dp.message(Registration.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    phone = message.text.strip().replace(' ', '')
    
    # Telefon raqamini tekshirish
    cleaned_phone = phone.replace('+', '')
    if not cleaned_phone.isdigit():
        await message.answer("❌ Telefon raqami faqat raqamlardan iborat bo'lishi kerak. Qaytadan kiriting:")
        return
    
    if len(cleaned_phone) < 9:
        await message.answer("❌ Telefon raqami juda qisqa. To'liq raqam kiriting:")
        return
    
    if not (cleaned_phone.startswith('998') or len(cleaned_phone) == 9):
        phone = f"+998{cleaned_phone[-9:]}" if len(cleaned_phone) == 9 else f"+{cleaned_phone}"
    
    await state.update_data(phone=phone)
    await state.set_state(Registration.waiting_for_description)
    
    await message.answer(f"""✅ Telefon raqami qabul qilindi.

5️⃣ **Ijodiy ishingiz haqida qisqacha ma'lumot** yuboring.
(Misol: *Boburning "Men sendin so'rayman..." g'azalini o'qiganman, video 1 daqiqa 45 soniya*)""")

# Tavsif qabul qilish va yakunlash
@dp.message(Registration.waiting_for_description)
async def process_description(message: Message, state: FSMContext):
    description = message.text.strip()
    
    if len(description) < 10:
        await message.answer("❌ Ijodiy ish haqida ma'lumot kamida 10 ta belgidan iborat bo'lishi kerak. Qaytadan kiriting:")
        return
    
    await state.update_data(description=description)
    
    # Barcha ma'lumotlarni olish
    data = await state.get_data()
    
    # Foydalanuvchi ma'lumotlari
    user = message.from_user
    username = user.username or "Noma'lum"
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    
    # Admin ga yuborish matni
    admin_text = f"""📥 **YANGI RO'YXATDAN O'TISH**

👤 **Foydalanuvchi:** @{username}
🆔 **ID:** `{user.id}`
📛 **Telegram nomi:** {full_name}
📞 **Telegram link:** https://t.me/{username if username != "Noma'lum" else ''}

📋 **MA'LUMOTLAR:**
1️⃣ **Ism-familiya:** {data['full_name']}
2️⃣ **Yosh:** {data['age']}
3️⃣ **Manzil:** {data['location']}
4️⃣ **Telefon:** {data['phone']}
5️⃣ **Ijodiy ish:** {data['description']}

⏰ **Vaqt:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    
    try:
        # Admin ga yuborish
        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_text
        )
        admin_notified = True
        logging.info(f"✅ Adminga yuborildi: {user.id} - @{username}")
    except Exception as e:
        admin_notified = False
        logging.error(f"Adminga yuborishda xato: {e}")
    
    # Foydalanuvchiga javob
    success_text = f"""✅ **Ro'yxatdan o'tish muvaffaqiyatli yakunlandi!**

📋 **Sizning ma'lumotlaringiz:**
• **Ism-familiya:** {data['full_name']}
• **Yosh:** {data['age']}
• **Manzil:** {data['location']}
• **Telefon:** {data['phone']}
• **Ijodiy ish:** {data['description'][:100]}...

👤 **Admin:** @{ADMIN_USERNAME}

📌 **Eslatma:** Ijodiy ishingizni @{ADMIN_USERNAME} ga yuboring."""

    # Admin bilan bog'lanish tugmasi
    contact_button = InlineKeyboardButton(text="👤 Admin bilan bog'lanish", url=f"https://t.me/{ADMIN_USERNAME}")
    contact_keyboard = InlineKeyboardMarkup(inline_keyboard=[[contact_button]])
    
    if admin_notified:
        success_text += "\n\n✅ Ma'lumotlaringiz adminga yuborildi."
    else:
        success_text += f"\n\n⚠️ Iltimos, @{ADMIN_USERNAME} ga aloqaga chiqing."
    
    await message.answer(success_text, reply_markup=contact_keyboard)
    await state.clear()

# Boshqa xabarlar
@dp.message()
async def handle_other_messages(message: Message):
    # Agar hech qanday holat bo'lmasa, startni qayta yuborish
    await start_cmd(message)

# Asosiy funksiya
async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Admin ma'lumotlarini saqlash
    save_admin_data()
    
    # Serverda mavjud fayllarni ko'rsatish
    logging.info("🤖 Bot ishga tushmoqda...")
    logging.info(f"👤 Admin: @{ADMIN_USERNAME} (ID: {ADMIN_CHAT_ID})")
    
    # Fayllarni tekshirish
    current_files = os.listdir('.')
    logging.info(f"📁 Mavjud fayllar: {current_files}")
    
    doc_file = check_file_exists(DOC_FILES)
    if doc_file:
        size = os.path.getsize(doc_file) / 1024
        logging.info(f"✅ DOCX fayl topildi: {doc_file} ({size:.1f} KB)")
    else:
        logging.warning("⚠️ DOCX fayl topilmadi")
    
    pdf_file = check_file_exists(PDF_FILES)
    if pdf_file:
        size = os.path.getsize(pdf_file) / 1024
        logging.info(f"✅ PDF fayl topildi: {pdf_file} ({size:.1f} KB)")
    else:
        logging.warning("⚠️ PDF fayl topilmadi")
    
    image_file = check_file_exists(IMAGE_FILES)
    if image_file:
        size = os.path.getsize(image_file) / 1024
        logging.info(f"✅ Rasm topildi: {image_file} ({size:.1f} KB)")
    else:
        logging.warning("⚠️ Rasm topilmadi")
    
    logging.info("🚀 Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
