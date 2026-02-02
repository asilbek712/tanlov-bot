import asyncio
import logging
import os
import json
import sqlite3
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile, ReplyKeyboardMarkup, KeyboardButton
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web

# TOKEN
TOKEN = "8483323640:AAF6ti4BpL3npCITChDPYoKP734VdjCIwug"
ADMIN_CHAT_ID = 8457390017  # @onlinetanlov_admin ID raqami
ADMIN_USERNAME = "onlinetanlov_admin"  # @onlinetanlov_admin username

# Bot yaratish
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# SQLite bazasini yaratish va connection boshqaruvi
class Database:
    def __init__(self):
        self.db_path = 'users.db'
        self.init_db()
    
    def init_db(self):
        """Bazani ishga tushirish"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Foydalanuvchilar jadvali
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS registered_users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            age INTEGER,
            location TEXT,
            phone TEXT,
            description TEXT,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """Yangi connection olish"""
        conn = sqlite3.connect(self.db_path)
        return conn
    
    def check_user_registered(self, user_id):
        """Foydalanuvchini bazadan tekshirish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM registered_users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        
        conn.close()
        return user is not None
    
    def add_user(self, user_data):
        """Foydalanuvchini bazaga qo'shish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO registered_users (user_id, username, full_name, age, location, phone, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_data['user_id'],
                user_data['username'],
                user_data['full_name'],
                user_data['age'],
                user_data['location'],
                user_data['phone'],
                user_data['description']
            ))
            
            conn.commit()
        except Exception as e:
            logging.error(f"Bazaga qo'shishda xato: {e}")
            raise
        finally:
            conn.close()
    
    def update_user_phone(self, user_id, phone):
        """Foydalanuvchi telefon raqamini yangilash"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('UPDATE registered_users SET phone = ? WHERE user_id = ?', 
                          (phone, user_id))
            
            conn.commit()
        except Exception as e:
            logging.error(f"Telefon yangilashda xato: {e}")
            raise
        finally:
            conn.close()
    
    def get_user_count(self):
        """Ro'yxatdan o'tganlar soni"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM registered_users')
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
    
    def get_all_users(self):
        """Barcha foydalanuvchilar (admin uchun)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT user_id, username, full_name, phone, registered_at FROM registered_users ORDER BY registered_at DESC')
        users = cursor.fetchall()
        
        conn.close()
        return users

# Global database obyekti
db = Database()

# FSM holatlari
class Registration(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_location = State()
    waiting_for_phone = State()
    waiting_for_description = State()

class PhoneRequest(StatesGroup):
    waiting_for_phone = State()

# Fayllar ro'yxatlari
IMAGE_FILES = [
    "bobur_poster.jpg",
    "poster.jpg",
    "tanlov_poster.jpg",
    "image.jpg",
    "bobur_poster.png"
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

# ==================== WEB SERVER (PORT 8080) ====================
async def handle_health_check(request):
    return web.Response(
        text="✅ Tanlov Bot ishlayapti!\n📅 Vaqt: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        content_type='text/plain'
    )

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_health_check)
    app.router.add_get('/health', handle_health_check)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    logging.info("🌐 Web server port 8080 da ishga tushdi")
    return runner

# ==================== YORDAMCHI FUNKSIYALAR ====================
def check_file_exists(file_list):
    for file_name in file_list:
        if os.path.exists(file_name):
            return file_name
    return None

def save_admin_data():
    data = {
        "admin_chat_id": ADMIN_CHAT_ID,
        "admin_username": ADMIN_USERNAME,
        "last_updated": datetime.now().isoformat()
    }
    with open("admin_config.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Telefon raqami tugmasini yaratish
def create_phone_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

# ==================== START FUNKSIYALARI ====================
START_TEXT = """📣 "BOBUR VORISLARI" VILOYAT ONLAYN VIDEOROLIKLAR TANLOVI

"Bobur vorislari" viloyat onlayn videoroliklar tanlovi o'tkaziladi...

📍 Qashqadaryo viloyat tuman, shahar "Kelajak" markazlari to'garak a'zolari o'rtasida Zahiriddin Muhammad Bobur tavalludining 543 yilligi munosabati bilan, uning hayoti va ijodi yuzasidan onlayn videoroliklar tanlovi tashkil etilmoqda.

🎯 **Maqsad:** Yosh avlodni ma'naviy tarbiyalash, ijodiy qobiliyatlarini rivojlantirish.

📅 **Sana:** 2026-yil 4-12 fevral

👥 **Qatnashuvchilar:** 8-18 yosh

📌 **Ijodiy ish shartlari:**
• Bobur ruboiylari yoki g'azallarini ifodali o'qish
• Yoki Bobur haqida ma'ruza tayyorlash
• Video: 2 daqiqa, 50 MB dan oshmasligi
• O'zbek tilida bo'lishi

🏆 **G'oliblar:** Diplom va sovg'alar bilan taqdirlanadi

📬 **Ijodiy ishlarni yuborish:** @onlinetanlov_admin

ℹ️ **Batafsil ma'lumot:** Quyidagi tugmalar orqali"""

@dp.message(Command("start"))
async def start_cmd(message: Message):
    user = message.from_user
    
    if user.id == ADMIN_CHAT_ID:
        logging.info(f"🔥 ADMIN KIRDI: @{user.username} (ID: {user.id})")
    
    # Foydalanuvchi allaqachon ro'yxatdan o'tganmi?
    if db.check_user_registered(user.id):
        # Agar ro'yxatdan o'tgan bo'lsa, maxsus menyu
        buttons = [
            [InlineKeyboardButton(text="📄 Tanlov nizomi (DOCX)", callback_data="download_doc")],
            [InlineKeyboardButton(text="📄 Tanlov nizomi (PDF)", callback_data="download_pdf")],
            [InlineKeyboardButton(text="📱 Telefon raqamni yangilash", callback_data="update_phone")],
            [InlineKeyboardButton(text="👤 Admin bilan bog'lanish", url=f"https://t.me/{ADMIN_USERNAME}")]
        ]
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        
        # Rasm mavjud bo'lsa
        image_file = check_file_exists(IMAGE_FILES)
        
        if image_file:
            try:
                photo = FSInputFile(image_file)
                await bot.send_photo(
                    chat_id=message.chat.id,
                    photo=photo,
                    caption=f"""✅ **Siz allaqachon ro'yxatdan o'tgansiz!**

{START_TEXT}

📌 **Eslatma:** Siz faqat bir marta ro'yxatdan o'tishingiz mumkin.
Agar telefon raqamingizni yangilash zarur bo'lsa, yuqoridagi tugmadan foydalaning.""",
                    reply_markup=keyboard
                )
            except Exception as e:
                logging.error(f"Rasm yuborishda xato: {e}")
                await message.answer(
                    f"""✅ **Siz allaqachon ro'yxatdan o'tgansiz!**

{START_TEXT}

📌 **Eslatma:** Siz faqat bir marta ro'yxatdan o'tishingiz mumkin.
Agar telefon raqamingizni yangilash zarur bo'lsa, yuqoridagi tugmadan foydalaning.""",
                    reply_markup=keyboard
                )
        else:
            await message.answer(
                f"""✅ **Siz allaqachon ro'yxatdan o'tgansiz!**

{START_TEXT}

📌 **Eslatma:** Siz faqat bir marta ro'yxatdan o'tishingiz mumkin.
Agar telefon raqamingizni yangilash zarur bo'lsa, yuqoridagi tugmadan foydalaning.""",
                reply_markup=keyboard
            )
        return
    
    # Agar ro'yxatdan o'tmagan bo'lsa, oddiy menyu
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
    
    # Admin uchun qo'shimcha tugmalar
    if user.id == ADMIN_CHAT_ID:
        buttons.append([InlineKeyboardButton(text="🆔 ID ni ko'rish", callback_data="show_id")])
        buttons.append([InlineKeyboardButton(text="📊 Statistika", callback_data="show_stats")])
        buttons.append([InlineKeyboardButton(text="👥 Ro'yxatdan o'tganlar", callback_data="show_users")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    # Rasm mavjud bo'lsa, rasm bilan yuborish
    image_file = check_file_exists(IMAGE_FILES)
    
    if image_file:
        try:
            photo = FSInputFile(image_file)
            await bot.send_photo(
                chat_id=message.chat.id,
                photo=photo,
                caption=START_TEXT,
                reply_markup=keyboard
            )
        except Exception as e:
            logging.error(f"Rasm yuborishda xato: {e}")
            await message.answer(START_TEXT, reply_markup=keyboard)
    else:
        await message.answer(START_TEXT, reply_markup=keyboard)

# ==================== ID FUNKSIYALARI ====================
@dp.message(Command("myid"))
async def myid_cmd(message: Message):
    user = message.from_user
    
    # APOSTROF MUAMMOSINI HAL QILISH
    username_display = f"@{user.username}" if user.username else "Yo'q"
    
    response = f"""🆔 **Sizning ma'lumotlaringiz:**
ID: `{user.id}`
Username: {username_display}
Ism: {user.first_name or ''}
Familiya: {user.last_name or ''}"""
    
    await message.answer(response)

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

# ==================== STATISTIKA FUNKSIYASI ====================
@dp.callback_query(F.data == "show_stats")
async def show_stats_cmd(callback: CallbackQuery):
    await callback.answer()
    user = callback.from_user
    
    if user.id == ADMIN_CHAT_ID:
        # Fayllarni tekshirish
        doc_file = check_file_exists(DOC_FILES)
        pdf_file = check_file_exists(PDF_FILES)
        image_file = check_file_exists(IMAGE_FILES)
        
        # Bazadan statistika
        total_users = db.get_user_count()
        
        stats_text = f"""📊 **Bot statistika:**

👥 **Ro'yxatdan o'tganlar:** {total_users} ta foydalanuvchi

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

# ==================== FOYDALANUVCHILARNI KO'RISH (ADMIN) ====================
@dp.callback_query(F.data == "show_users")
async def show_users_cmd(callback: CallbackQuery):
    await callback.answer()
    user = callback.from_user
    
    if user.id == ADMIN_CHAT_ID:
        users = db.get_all_users()
        
        if not users:
            await callback.message.answer("📭 Hali hech kim ro'yxatdan o'tmagan.")
            return
        
        text = f"👥 **Ro'yxatdan o'tganlar ({len(users)} ta):**\n\n"
        
        for idx, user_data in enumerate(users[:20], 1):  # Birinchi 20 tasini ko'rsatish
            user_id, username, full_name, phone, registered_at = user_data
            text += f"{idx}. {full_name}\n"
            text += f"   👤 @{username or 'Noma\'lum'}\n"
            text += f"   🆔 {user_id}\n"
            text += f"   📱 {phone}\n"
            text += f"   📅 {registered_at}\n\n"
        
        if len(users) > 20:
            text += f"\n⚠️ Faqat birinchi 20 ta ko'rsatilmoqda. Jami: {len(users)} ta"
        
        await callback.message.answer(text)

# ==================== FAYL YUKLASH FUNKSIYALARI ====================
@dp.callback_query(F.data == "download_doc")
async def download_doc_cmd(callback: CallbackQuery):
    await callback.answer("📥 Yuklanmoqda...")
    
    doc_file = check_file_exists(DOC_FILES)
    
    if doc_file:
        try:
            doc_obj = FSInputFile(doc_file)
            await bot.send_document(
                chat_id=callback.message.chat.id,
                document=doc_obj,
                caption="📄 **Tanlov nizomi**\nFaylni yuklab oling va o'qing."
            )
        except Exception as e:
            logging.error(f"DOCX yuklashda xato: {e}")
            await callback.message.answer(f"❌ Fayl yuklashda xatolik\n\n👤 Admin bilan bog'laning: @{ADMIN_USERNAME}")
    else:
        await callback.message.answer(
            f"❌ Nizom fayli topilmadi.\n\n"
            f"👤 Admin bilan bog'laning: @{ADMIN_USERNAME}"
        )

@dp.callback_query(F.data == "download_pdf")
async def download_pdf_cmd(callback: CallbackQuery):
    await callback.answer("📥 Yuklanmoqda...")
    
    pdf_file = check_file_exists(PDF_FILES)
    
    if pdf_file:
        try:
            pdf_obj = FSInputFile(pdf_file)
            await bot.send_document(
                chat_id=callback.message.chat.id,
                document=pdf_obj,
                caption="📄 **Tanlov nizomi (PDF)**\nFaylni yuklab oling va o'qing."
            )
        except Exception as e:
            logging.error(f"PDF yuklashda xato: {e}")
            await callback.message.answer(f"❌ Fayl yuklashda xatolik\n\n👤 Admin bilan bog'laning: @{ADMIN_USERNAME}")
    else:
        await callback.message.answer(
            f"❌ PDF fayli topilmadi.\n\n"
            f"👤 Admin bilan bog'laning: @{ADMIN_USERNAME}"
        )

# ==================== TELEFON RAQAMNI YANGILASH ====================
@dp.callback_query(F.data == "update_phone")
async def update_phone_cmd(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    # Foydalanuvchi ro'yxatdan o'tganmi?
    if not db.check_user_registered(callback.from_user.id):
        await callback.message.answer("❌ Siz hali ro'yxatdan o'tmagansiz. Avval ro'yxatdan o'ting.")
        return
    
    await state.set_state(PhoneRequest.waiting_for_phone)
    
    await callback.message.answer(
        "📱 **Yangi telefon raqamingizni yuboring:**\n\n"
        "Telefon raqamingizni quyidagi tugma orqali yuboring yoki formatda kiriting:\n"
        "Misol: *+998901234567* yoki *901234567*",
        reply_markup=create_phone_keyboard()
    )

@dp.message(PhoneRequest.waiting_for_phone)
async def process_update_phone(message: Message, state: FSMContext):
    # Contact yuborilganmi?
    if message.contact:
        phone = message.contact.phone_number
    else:
        phone = message.text.strip().replace(' ', '')
    
    # Telefon raqamini tekshirish va formatlash
    cleaned_phone = phone.replace('+', '')
    if not cleaned_phone.isdigit():
        await message.answer("❌ Telefon raqami faqat raqamlardan iborat bo'lishi kerak. Qaytadan kiriting:",
                           reply_markup=create_phone_keyboard())
        return
    
    if len(cleaned_phone) < 9:
        await message.answer("❌ Telefon raqami juda qisqa. To'liq raqam kiriting:",
                           reply_markup=create_phone_keyboard())
        return
    
    if not (cleaned_phone.startswith('998') or len(cleaned_phone) == 9):
        phone = f"+998{cleaned_phone[-9:]}" if len(cleaned_phone) == 9 else f"+{cleaned_phone}"
    
    try:
        # Bazaga yangilash
        db.update_user_phone(message.from_user.id, phone)
        
        await message.answer(
            f"✅ **Telefon raqamingiz muvaffaqiyatli yangilandi!**\n\n"
            f"📱 **Yangi raqam:** {phone}\n\n"
            f"👤 **Admin:** @{ADMIN_USERNAME}",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="/start")]],
                resize_keyboard=True
            )
        )
        
        # Admin ga bildirish
        try:
            await bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=f"📱 **Telefon raqam yangilandi**\n\n"
                     f"👤 Foydalanuvchi: @{message.from_user.username or 'Noma\'lum'}\n"
                     f"🆔 ID: `{message.from_user.id}`\n"
                     f"📱 Yangi raqam: {phone}\n"
                     f"⏰ Vaqt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
        except Exception as e:
            logging.error(f"Adminga xabar yuborishda xato: {e}")
    
    except Exception as e:
        logging.error(f"Telefon raqam yangilashda xato: {e}")
        await message.answer("❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring yoki admin bilan bog'laning.")
    
    await state.clear()

# ==================== RO'YXATDAN O'TISH FUNKSIYALARI ====================
@dp.callback_query(F.data == "start_registration")
async def start_registration_cmd(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    # Foydalanuvchi allaqachon ro'yxatdan o'tganmi?
    if db.check_user_registered(callback.from_user.id):
        await callback.message.answer(
            "❌ **Siz allaqachon ro'yxatdan o'tgansiz!**\n\n"
            "Siz faqat bir marta ro'yxatdan o'tishingiz mumkin.\n"
            "Agar telefon raqamingizni yangilash zarur bo'lsa, /start ni bosing va 'Telefon raqamni yangilash' tugmasidan foydalaning."
        )
        return
    
    await state.set_state(Registration.waiting_for_name)
    
    text = """🎯 **Ro'yxatdan o'tish**

Quyidagi ma'lumotlarni ketma-ket yuboring:

1️⃣ **Ism va familiyangizni** yuboring.
(Misol: *Alisher Navoiy*)"""
    
    await callback.message.answer(text)

@dp.message(Registration.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip()
    
    if len(name) < 3:
        await message.answer("❌ Ism va familiya kamida 3 ta belgidan iborat bo'lishi kerak. Qaytadan kiriting:")
        return
    
    await state.update_data(full_name=name)
    await state.set_state(Registration.waiting_for_age)
    
    await message.answer(f"""✅ *{name}* qabul qilindi.

2️⃣ **Yoshingizni** yuboring (8-18 yosh oralig'ida).
(Misol: *15*)""")

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

📱 **Iltimos, telefon raqamingizni quyidagi tugma orqali yuboring:**""",
        reply_markup=create_phone_keyboard()
    )

@dp.message(Registration.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    # Contact yuborilganmi?
    if message.contact:
        phone = message.contact.phone_number
    else:
        phone = message.text.strip().replace(' ', '')
    
    # Telefon raqamini tekshirish va formatlash
    cleaned_phone = phone.replace('+', '')
    if not cleaned_phone.isdigit():
        await message.answer("❌ Telefon raqami faqat raqamlardan iborat bo'lishi kerak. Qaytadan kiriting:",
                           reply_markup=create_phone_keyboard())
        return
    
    if len(cleaned_phone) < 9:
        await message.answer("❌ Telefon raqami juda qisqa. To'liq raqam kiriting:",
                           reply_markup=create_phone_keyboard())
        return
    
    if not (cleaned_phone.startswith('998') or len(cleaned_phone) == 9):
        phone = f"+998{cleaned_phone[-9:]}" if len(cleaned_phone) == 9 else f"+{cleaned_phone}"
    
    await state.update_data(phone=phone)
    await state.set_state(Registration.waiting_for_description)
    
    await message.answer(f"""✅ Telefon raqami qabul qilindi.

5️⃣ **Ijodiy ishingiz haqida qisqacha ma'lumot** yuboring.
(Misol: *Boburning "Men sendin so'rayman..." g'azalini o'qiganman, video 1 daqiqa 45 soniya*)""",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Davom etish")]],
            resize_keyboard=True
        )
    )

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
    
    # Bazaga saqlash
    user_data = {
        'user_id': user.id,
        'username': username,
        'full_name': data['full_name'],
        'age': data['age'],
        'location': data['location'],
        'phone': data['phone'],
        'description': data['description']
    }
    
    try:
        db.add_user(user_data)
        save_success = True
    except Exception as e:
        logging.error(f"Bazaga saqlashda xato: {e}")
        save_success = False
    
    if save_success:
        # Admin ga yuborish matni
        admin_text = f"""📥 **YANGI RO'YXATDAN O'TISH**

👤 **Foydalanuvchi:** @{username}
🆔 **ID:** `{user.id}`
📛 **Telegram nomi:** {user.first_name or ''} {user.last_name or ''}

📋 **MA'LUMOTLAR:**
1️⃣ **Ism-familiya:** {data['full_name']}
2️⃣ **Yosh:** {data['age']}
3️⃣ **Manzil:** {data['location']}
4️⃣ **Telefon:** {data['phone']}
5️⃣ **Ijodiy ish:** {data['description']}

⏰ **Vaqt:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
👥 **Jami ro'yxatdan o'tganlar:** {db.get_user_count()}"""
        
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

📌 **Eslatma:** Ijodiy ishingizni @{ADMIN_USERNAME} ga yuboring.

⚠️ **Diqqat:** Siz endi qayta ro'yxatdan o'ta olmaysiz. Faqat telefon raqamingizni yangilashingiz mumkin."""
    else:
        success_text = f"""❌ **Ro'yxatdan o'tishda xatolik yuz berdi!**

Iltimos, qayta urinib ko'ring yoki admin bilan bog'laning.

👤 **Admin:** @{ADMIN_USERNAME}"""
        admin_notified = False
    
    # Admin bilan bog'lanish tugmasi
    contact_button = InlineKeyboardButton(text="👤 Admin bilan bog'lanish", url=f"https://t.me/{ADMIN_USERNAME}")
    contact_keyboard = InlineKeyboardMarkup(inline_keyboard=[[contact_button]])
    
    if admin_notified:
        success_text += "\n\n✅ Ma'lumotlaringiz adminga yuborildi."
    else:
        success_text += f"\n\n⚠️ Iltimos, @{ADMIN_USERNAME} ga aloqaga chiqing."
    
    await message.answer(success_text, reply_markup=contact_keyboard)
    await state.clear()

# ==================== BOSHQA XABARLAR ====================
@dp.message()
async def handle_other_messages(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        # Agar ro'yxatdan o'tish jarayonida bo'lmasa, start qayta yuborish
        await start_cmd(message)
    else:
        # Agar ro'yxatdan o'tish jarayonida bo'lsa
        await message.answer("⚠️ Siz ro'yxatdan o'tish jarayonidasiz. Davom eting yoki /start ni bosing.")

# ==================== ASOSIY FUNKSIYA ====================
async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Admin ma'lumotlarini saqlash
    save_admin_data()
    
    # Log boshlash
    logging.info("🚀 ===== BOT ISHGA TUSHMOQDA =====")
    
    # Fayllarni tekshirish
    current_files = os.listdir('.')
    logging.info(f"📁 Mavjud fayllar: {len(current_files)} ta")
    
    # Fayllarni ko'rsatish
    doc_file = check_file_exists(DOC_FILES)
    if doc_file:
        size = os.path.getsize(doc_file) / 1024
        logging.info(f"✅ DOCX fayl: {doc_file} ({size:.1f} KB)")
    else:
        logging.warning("⚠️ DOCX fayl topilmadi")
    
    pdf_file = check_file_exists(PDF_FILES)
    if pdf_file:
        size = os.path.getsize(pdf_file) / 1024
        logging.info(f"✅ PDF fayl: {pdf_file} ({size:.1f} KB)")
    else:
        logging.warning("⚠️ PDF fayl topilmadi")
    
    image_file = check_file_exists(IMAGE_FILES)
    if image_file:
        size = os.path.getsize(image_file) / 1024
        logging.info(f"✅ Rasm: {image_file} ({size:.1f} KB)")
    else:
        logging.warning("⚠️ Rasm topilmadi")
    
    # Baza statistikasi
    user_count = db.get_user_count()
    
    logging.info(f"👥 Ro'yxatdan o'tganlar: {user_count} ta")
    logging.info(f"👤 Admin: @{ADMIN_USERNAME} (ID: {ADMIN_CHAT_ID})")
    logging.info("🌐 Web server ishga tushmoqda...")
    
    # Web server ishga tushirish
    web_server = await start_web_server()
    
    logging.info("🤖 Bot polling boshlandi...")
    
    try:
        # Bot polling ni ishga tushirish
        await dp.start_polling(bot)
    finally:
        # Tozalash
        await web_server.cleanup()
        logging.info("👋 Bot to'xtatildi")

if __name__ == "__main__":
    asyncio.run(main())
