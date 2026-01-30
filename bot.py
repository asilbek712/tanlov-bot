import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile, ReplyKeyboardRemove
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

# TOKEN
TOKEN = "8483323640:AAF6ti4BpL3npCITChDPYoKP734VdjCIwug"
ADMIN_USERNAME = "chrvvvv"

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

# Rasm fayllari ro'yxati
IMAGE_FILES = [
    "bobur_poster.jpg",
    "bobur_poster.png",
    "poster.jpg",
    "poster.png",
    "tanlov_rasmi.jpg",
    "tanlov_rasmi.png"
]

# Fayl mavjudligini tekshirish
def check_file_exists(file_list):
    for file_name in file_list:
        if os.path.exists(file_name):
            return file_name
    return None

# /start
@dp.message(Command("start"))
async def start_cmd(message: Message):
    # Rasm mavjudligini tekshirish
    image_file = check_file_exists(IMAGE_FILES)
    
    # Tanlov nizomi fayli
    doc_file = check_file_exists(["bobur_nizomi.docx", "14-fevral Zahriddin Muxammad Bobur.docx"])
    
    # Havola tugmalari
    buttons = []
    
    # Nizomni yuklash tugmasi
    if doc_file:
        button_doc = InlineKeyboardButton(text="📄 Tanlov nizomini yuklab olish", callback_data="download_doc")
        buttons.append([button_doc])
    
    # Ro'yxatdan o'tish tugmasi
    button_register = InlineKeyboardButton(text="📝 Ro'yxatdan o'tish", callback_data="start_registration")
    buttons.append([button_register])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    # Rasm mavjud bo'lsa, rasm bilan matn yuborish
    if image_file:
        try:
            photo = FSInputFile(image_file)
            caption = """📣 🔤🔤🔤🔤🔤🔤📣

"Bobur vorislari" viloyat onlayn videoroliklar tanlovi o‘tkaziladi... 

📍Qashqadaryo viloyat tuman, shahar "Kelajak" markazlari to‘garak aʼzolari o‘rtasida Zahiriddin Muhammad Bobur tavalludining 543 yilligi munosabati bilan, uning hayoti va ijodi yuzasidan onlayn videoroliklar tanlovi tashkil etilmoqda. 

⬇️Mazkur tanlov: 
◾️viloyat tuman, shahar "Kelajak" markazlari to‘garak aʼzolari; 
◾️umumiy o‘rta taʼlim maktabi o‘quvchilari o‘rtasida o‘tkaziladi. 

📌Onlayn videorolik tanlov nizomi bilan batafsil quyidagi havola tanishing!

👏Tanlov g‘oliblari viloyat "Kelajak" markazi tomonidan maxsus diplom va esdalik sovg‘alari bilan taqdirlanadi.

🗓Tanlov:
😐2026-yil 4-fevral kunidan 12- fevral kuniga qadar "Bobur vorislari" sarlavhasi ostida @tanlov2026_bot telegram botida o‘tkaziladi.
😐Ijodiy ishlarni @chrvvvv telegram manziliga yuborishingiz so‘raladi.

🔘Tanlovning asosiy maqsadi:
✅ To‘garak aʼzolari hamda o‘quvchi-yoshlarning shoh va shoir Bobur hayoti va ijodiga qiziqishini oshirish, ularni maʼnaviy-maʼrifiy ruhda tarbiyalash, nutq madaniyati va axborot texnologiyalardan foydalanish ko‘nikmalarini rivojlantirishdan iborat. 

Maʼlumot uchun: 
Qatnashchilar videorolik tayyorlash jarayonida Bobur ruboiylari, g‘azallaridan birini ifodali o‘qib berishi yoki shoh va shoir haqida maʼruza tayyorlashi, olinadigan video esa 2 daqiqa, 50 mb oshmasligi lozim. 

Qashqadaryo viloyat "Kelajak" markazi 
🌍🌍🌍🌍🌍🌍"""
            
            await message.answer_photo(
                photo=photo,
                caption=caption,
                reply_markup=keyboard
            )
            return
        except Exception as e:
            logging.error(f"Rasm yuborishda xato: {e}")
    
    # Rasm mavjud bo'lmasa faqat matn
    start_text = """📣 🔤🔤🔤🔤🔤🔤📣

"Bobur vorislari" viloyat onlayn videoroliklar tanlovi o‘tkaziladi... 

📍Qashqadaryo viloyat tuman, shahar "Kelajak" markazlari to‘garak aʼzolari o‘rtasida Zahiriddin Muhammad Bobur tavalludining 543 yilligi munosabati bilan, uning hayoti va ijodi yuzasidan onlayn videoroliklar tanlovi tashkil etilmoqda. 

⬇️Mazkur tanlov: 
◾️viloyat tuman, shahar "Kelajak" markazlari to‘garak aʼzolari; 
◾️umumiy o‘rta taʼlim maktabi o‘quvchilari o‘rtasida o‘tkaziladi. 

📌Onlayn videorolik tanlov nizomi bilan batafsil quyidagi havola tanishing!

👏Tanlov g‘oliblari viloyat "Kelajak" markazi tomonidan maxsus diplom va esdalik sovg‘alari bilan taqdirlanadi.

🗓Tanlov:
😐2026-yil 4-fevral kunidan 12- fevral kuniga qadar "Bobur vorislari" sarlavhasi ostida @tanlov2026_bot telegram botida o‘tkaziladi.
😐Ijodiy ishlarni @chrvvvv telegram manziliga yuborishingiz so‘raladi.

🔘Tanlovning asosiy maqsadi:
✅ To‘garak aʼzolari hamda o‘quvchi-yoshlarning shoh va shoir Bobur hayoti va ijodiga qiziqishini oshirish, ularni maʼnaviy-maʼrifiy ruhda tarbiyalash, nutq madaniyati va axborot texnologiyalardan foydalanish ko‘nikmalarini rivojlantirishdan iborat. 

Maʼlumot uchun: 
Qatnashchilar videorolik tayyorlash jarayonida Bobur ruboiylari, g‘azallaridan birini ifodali o‘qib berishi yoki shoh va shoir haqida maʼruza tayyorlashi, olinadigan video esa 2 daqiqa, 50 mb oshmasligi lozim. 

Qashqadaryo viloyat "Kelajak" markazi 
🌍🌍🌍🌍🌍🌍"""
    
    await message.answer(start_text, reply_markup=keyboard)

# Faylni yuklash uchun callback
@dp.callback_query(F.data == "download_doc")
async def download_doc_cmd(callback: CallbackQuery):
    await callback.answer()
    
    doc_file = check_file_exists(["bobur_nizomi.docx", "14-fevral Zahriddin Muxammad Bobur.docx"])
    if doc_file:
        try:
            doc_file_obj = FSInputFile(doc_file)
            await callback.message.answer_document(
                document=doc_file_obj, 
                caption="📄 Tanlov nizomi"
            )
        except Exception as e:
            logging.error(f"Fayl yuklashda xato: {e}")
            await callback.message.answer("❌ Fayl yuklashda xatolik yuz berdi. Admin bilan bog'laning.")
    else:
        await callback.message.answer("❌ Fayl topilmadi. Admin bilan bog'laning.")

# Ro'yxatdan o'tishni boshlash
@dp.callback_query(F.data == "start_registration")
async def start_registration_cmd(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Registration.waiting_for_name)
    
    # Admin profiliga havola tugmasi
    admin_button = InlineKeyboardButton(text="👤 Admin bilan bog'lanish", url=f"https://t.me/{ADMIN_USERNAME}")
    admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[[admin_button]])
    
    text = """🎯 Ro'yxatdan o'tishni boshlash uchun quyidagi ma'lumotlarni ketma-ket yuboring:

1️⃣ Birinchi: **Ism va familiyangizni** yuboring.
(Misol: Alisher Navoiy)"""
    
    await callback.message.answer(text, reply_markup=admin_keyboard)

# Ism qabul qilish
@dp.message(Registration.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    if len(message.text.strip()) < 3:
        await message.answer("❌ Ism va familiya kamida 3 ta belgidan iborat bo'lishi kerak. Qaytadan kiriting:")
        return
    
    await state.update_data(full_name=message.text.strip())
    await state.set_state(Registration.waiting_for_age)
    
    text = """✅ Ism va familiya qabul qilindi.

2️⃣ Ikkinchi: **Yoshingizni** yuboring (8-18 yosh oralig'ida).
(Misol: 15)"""
    
    await message.answer(text)

# Yosh qabul qilish
@dp.message(Registration.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
    try:
        age = int(message.text.strip())
        if age < 8 or age > 18:
            await message.answer("❌ Yosh 8 dan 18 gacha bo'lishi kerak. Qaytadan kiriting:")
            return
    except ValueError:
        await message.answer("❌ Yosh raqam bo'lishi kerak. Qaytadan kiriting:")
        return
    
    await state.update_data(age=age)
    await state.set_state(Registration.waiting_for_location)
    
    text = """✅ Yosh qabul qilindi.

3️⃣ Uchinchi: **Manzilingizni** yuboring (shahar/tuman).
(Misol: Qarshi shahri)"""
    
    await message.answer(text)

# Manzil qabul qilish
@dp.message(Registration.waiting_for_location)
async def process_location(message: Message, state: FSMContext):
    if len(message.text.strip()) < 3:
        await message.answer("❌ Manzil kamida 3 ta belgidan iborat bo'lishi kerak. Qaytadan kiriting:")
        return
    
    await state.update_data(location=message.text.strip())
    await state.set_state(Registration.waiting_for_phone)
    
    text = """✅ Manzil qabul qilindi.

4️⃣ To'rtinchi: **Telefon raqamingizni** yuboring.
(Misol: +998901234567)"""
    
    await message.answer(text)

# Telefon qabul qilish
@dp.message(Registration.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    if not phone.replace('+', '').isdigit() or len(phone) < 9:
        await message.answer("❌ Telefon raqami to'g'ri formatda emas. Qaytadan kiriting:")
        return
    
    await state.update_data(phone=phone)
    await state.set_state(Registration.waiting_for_description)
    
    text = """✅ Telefon raqami qabul qilindi.

5️⃣ Beshinchi: **Ijodiy ishingiz haqida qisqacha ma'lumot** yuboring.
(Misol: Boburning "Men sendin so'rayman..." g'azalini o'qiganman, video 1 daqiqa 45 soniya)"""
    
    await message.answer(text)

# Tavsif qabul qilish va yakunlash
@dp.message(Registration.waiting_for_description)
async def process_description(message: Message, state: FSMContext):
    if len(message.text.strip()) < 10:
        await message.answer("❌ Ijodiy ish haqida ma'lumot kamida 10 ta belgidan iborat bo'lishi kerak. Qaytadan kiriting:")
        return
    
    await state.update_data(description=message.text.strip())
    
    # Barcha ma'lumotlarni olish
    data = await state.get_data()
    
    # Foydalanuvchi ma'lumotlari
    user = message.from_user
    username = user.username or "Noma'lum"
    
    # Admin ga yuborish
    admin_text = f"""📥 YANGI RO'YXATDAN O'TISH

👤 **Foydalanuvchi:** @{username}
🆔 **ID:** {user.id}
📞 **Telegram:** https://t.me/{username}

📋 **MA'LUMOTLAR:**
1️⃣ **Ism-familiya:** {data['full_name']}
2️⃣ **Yosh:** {data['age']}
3️⃣ **Manzil:** {data['location']}
4️⃣ **Telefon:** {data['phone']}
5️⃣ **Ijodiy ish:** {data['description']}

⏰ **Ro'yxatdan o'tish vaqti:** {message.date.strftime('%Y-%m-%d %H:%M:%S')}"""
    
    try:
        # Admin ga yuborish
        admin_button = InlineKeyboardButton(text="👤 Profilga o'tish", url=f"https://t.me/{ADMIN_USERNAME}")
        admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[[admin_button]])
        
        await bot.send_message(
            chat_id=ADMIN_USERNAME,
            text=admin_text,
            reply_markup=admin_keyboard
        )
    except Exception as e:
        logging.error(f"Admin ga yuborishda xato: {e}")
    
    # Foydalanuvchiga javob
    success_text = f"""✅ **Ro'yxatdan o'tish muvaffaqiyatli yakunlandi!**

📋 **Sizning ma'lumotlaringiz:**
• **Ism-familiya:** {data['full_name']}
• **Yosh:** {data['age']}
• **Manzil:** {data['location']}
• **Telefon:** {data['phone']}
• **Ijodiy ish:** {data['description'][:50]}...

👤 **Admin bilan bog'lanish:** @{ADMIN_USERNAME}

📌 **Eslatma:** Ijodiy ishingizni @{ADMIN_USERNAME} ga yuboring. Tanlov natijalari telegram orqali e'lon qilinadi."""

    # Admin bilan bog'lanish tugmasi
    contact_button = InlineKeyboardButton(text="👤 Admin bilan bog'lanish", url=f"https://t.me/{ADMIN_USERNAME}")
    contact_keyboard = InlineKeyboardMarkup(inline_keyboard=[[contact_button]])
    
    await message.answer(success_text, reply_markup=contact_keyboard)
    await state.clear()

# Boshqa xabarlar (ro'yxatdan o'tish jarayonida emas)
@dp.message()
async def handle_other_messages(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        # Agar ro'yxatdan o'tish jarayonida bo'lmasa, start qayta yuborish
        await start_cmd(message)
    else:
        # Agar ro'yxatdan o'tish jarayonida bo'lsa, qayta boshlash tugmasi
        restart_button = InlineKeyboardButton(text="🔄 Ro'yxatdan o'tishni qayta boshlash", callback_data="start_registration")
        cancel_button = InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_registration")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[restart_button], [cancel_button]])
        
        await message.answer("⚠️ Siz ro'yxatdan o'tish jarayonidasiz. Davom etish yoki qayta boshlash uchun tugmalardan foydalaning.", reply_markup=keyboard)

# Ro'yxatdan o'tishni bekor qilish
@dp.callback_query(F.data == "cancel_registration")
async def cancel_registration_cmd(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.answer("❌ Ro'yxatdan o'tish bekor qilindi.")

# Asosiy funksiya
async def main():
    logging.basicConfig(level=logging.INFO)
    
    # Serverda mavjud fayllarni ko'rsatish
    current_files = os.listdir('.')
    logging.info(f"Mavjud fayllar: {current_files}")
    
    # Rasm fayllari mavjudligini tekshirish
    for img in IMAGE_FILES:
        if os.path.exists(img):
            logging.info(f"Rasm topildi: {img}")
    
    # DOCX fayl mavjudligini tekshirish
    doc_file = check_file_exists(["bobur_nizomi.docx", "14-fevral Zahriddin Muxammad Bobur.docx"])
    if doc_file:
        logging.info(f"DOCX fayl topildi: {doc_file}")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
