import asyncio
import logging
import json
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, Message,
    InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
)

# -------------------------------------------------------------------
# 1. SOZLAMALAR
# -------------------------------------------------------------------
BOT_TOKEN = "8930238377:AAHwD1OLdLWXykUtyUv1_tNhZtrz_2L0Srw"
ADMIN_ID = 1774408231

# Sizning karta raqamingiz
CARD_NUMBER = "986017013008445"  

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Ma'lumotlar bazasi fayllari
DB_FILE = "books_db.json"
USERS_FILE = "users_db.json"

def load_data(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

BOOKS_DATABASE = load_data(DB_FILE)
USERS_DATABASE = load_data(USERS_FILE)

# -------------------------------------------------------------------
# 2. VILOYATLAR VA TUMANLAR
# -------------------------------------------------------------------
REGIONS = {
    "Toshkent shahri": [
        "Bektemir t.", "Chilonzor t.", "Yashnobod t.", "Mirobod t.", "Mirzo Ulug'bek t.", 
        "Olmazor t.", "Sergeli t.", "Shayxontohur t.", "Uchtepa t.", "Yakkasaroy t.", 
        "Yunusobod t.", "Yangihayot t."
    ],
    "Toshkent viloyati": [
        "Olmaliq sh.", "Angren sh.", "Bekobod sh.", "Chirchiq sh.", "Nurafshon sh.", "Yangiyo'l sh.",
        "Oqqo'rg'on t.", "Ohangaron t.", "Bekobod t.", "Bo'stonliq t.", "Bo'ka t.", "Zangiota t.",
        "Qibray t.", "Parkent t.", "Piskent t.", "Quyi Chirchiq t.", "O'rta Chirchiq t.", 
        "Yangiqo'rg'on t.", "Chinoz t.", "Yangiyo'l t.", "Toshkent t."
    ],
    "Andijon viloyati": [
        "Andijon sh.", "Xonobod sh.", "Andijon t.", "Asaka t.", "Baliqchi t.", "Bo'ston t.",
        "Buloqboshi t.", "Jalaquduq t.", "Izboskan t.", "Marhamat t.", "Oltinko'l t.", 
        "Paxtaobod t.", "Ulug'nor t.", "Xo'jaobod t.", "Shahrixon t.", "Qo'rg'ontepa t."
    ],
    "Buxoro viloyati": [
        "Buxoro sh.", "Kogon sh.", "Olot t.", "Buxoro t.", "Vobkent t.", "G'ijduvon t.",
        "Jondor t.", "Kogon t.", "Qorako'l t.", "Qoraulpazar t.", "Peshku t.", "Romitan t.", "Shofirkon t."
    ],
    "Farg'ona viloyati": [
        "Farg'ona sh.", "Marg'ilon sh.", "Qo'qon sh.", "Quvasoy sh.", "Beshariq t.",
        "Bog'dod t.", "Buvayda t.", "Dang'ara t.", "Yozyovon t.", "Oltiariq t.", "Qo'shtepa t.",
        "Rishton t.", "So'x t.", "Toshloq t.", "Uchko'prik t.", "Farg'ona t.", "Furqat t.", "Quva t."
    ],
    "Jizzax viloyati": [
        "Jizzax sh.", "Arnasoy t.", "Baxmal t.", "G'allaorol t.", "Do'stlik t.", "Zomin t.",
        "Zarbdor t.", "Zafarobod t.", "Mirzacho'l t.", "Paxtakor t.", "Forish t.", "Sharof Rashidov t."
    ],
    "Xorazm viloyati": [
        "Urganch sh.", "Xiva sh.", "Bog'ot t.", "Gurlan t.", "Qushko'pir t.", "Tuproqqal'a t.",
        "Hazorasp t.", "Xonqa t.", "Xiva t.", "Shovot t.", "Yangiariq t.", "Yangibozor t.", "Urganch t."
    ],
    "Namangan viloyati": [
        "Namangan sh.", "Mingbuloq t.", "Kosonsoy t.", "Norin t.", "Pop t.", "To'raqo'rg'on t.",
        "Uychi t.", "Uchqo'rg'on t.", "Chortoq t.", "Chust t.", "Yangiqo'rg'on t.", 
        "Davlatobod t.", "Yangi Namangan t."
    ],
    "Navoiy viloyati": [
        "Navoiy sh.", "Zarafshon sh.", "Konimex t.", "Karmana t.", "Qiziltepa t.", "Xatirchi t.",
        "Navbahor t.", "Nurota t.", "Tomdi t.", "Uchquduq t."
    ],
    "Qashqadaryo viloyati": [
        "Qarshi sh.", "Shahrisabz sh.", "G'uzor t.", "Dehqonobod t.", "Qamashi t.", "Qarshi t.",
        "Koson t.", "Kasbi t.", "Kitob t.", "Mirishkor t.", "Muborak t.", "Nishan t.", 
        "Chiroqchi t.", "Shahrisabz t.", "Yakkabog' t.", "Ko'kdala t."
    ],
    "Samarqand viloyati": [
        "Samarqand sh.", "Kattaqo'rg'on sh.", "Oqdaryo t.", "Bulung'ur t.", "Jomboy t.",
        "Ishtixon t.", "Kattaqo'rg'on t.", "Qoshrabot t.", "Narpay t.", "Nurobod t.", "Payariq t.",
        "Pastdarg'om t.", "Paxtachi t.", "Samarqand t.", "Toyloq t.", "Urgut t."
    ],
    "Sirdaryo viloyati": [
        "Guliston sh.", "Shirin sh.", "Yangiyer sh.", "Oqoltin t.", "Boyovut t.",
        "Guliston t.", "Xovos t.", "Mirzaobod t.", "Sardoba t.", "Sayxunobod t.", "Sirdaryo t."
    ],
    "Surxondaryo viloyati": [
        "Termiz sh.", "Angor t.", "Bandixon t.", "Boysun t.", "Denov t.", "Jarkurg'on t.",
        "Qiziriq t.", "Qumqo'rg'on t.", "Muzrabot t.", "Oltinsoy t.", "Sariosiyo t.", 
        "Termiz t.", "Uzun t.", "Sherobod t."
    ],
    "Qoraqalpog'iston Resp.": [
        "Nukus sh.", "Amudaryo t.", "Beruniy t.", "Chimboy t.", "Ellikqala t.", "Kegeyli t.",
        "Mo'ynoq t.", "Nukus t.", "Qonliko'l t.", "Qorao'zak t.", "Shumanay t.", 
        "Taxtako'pir t.", "To'rtko'l t.", "Xo'jayli t.", "Bo'zatov t.", "Taqiatosh t."
    ]
}

TEXTS = {
    'uz': {
        'enter_fullname': "Ismingiz, familiyangiz va otangizning ismini (F.I.O.) to'liq kiriting:\n(Masalan: Islomov Anvar Jamshidovich)",
        'choose_region': "Viloyatingizni tanlang:",
        'choose_district': "Tumaningizni tanlang:",
        'enter_mahalla': "Mahallangiz nomini yozing:",
        'send_phone': "Telefon raqamingizni yuboring:",
        'phone_btn': "📱 Telefon raqamni yuborish",
        'main_menu': "Asosiy menyuga xush kelibsiz! Kerakli bo'limni tanlang yoki kitob nomini yozing:",
        'book_not_found': "Kechirasiz, bunday kitob topilmadi.",
        'sending_book': "Kitob yuborilmoqda, kuting..."
    }
}

class UserRegistration(StatesGroup):
    language = State()
    fullname = State()
    region = State()
    district = State()
    mahalla = State()
    phone = State()
    main_menu = State()

def main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👤 Hisobim"), KeyboardButton(text="💰 Balans")],
            [KeyboardButton(text="💳 To'lov qilish")]
        ],
        resize_keyboard=True
    )

# -------------------------------------------------------------------
# 3. ADMIN KODLARI VA BALANS OSHIRISH
# -------------------------------------------------------------------
@dp.message(F.document, F.from_user.id == ADMIN_ID)
async def admin_add_book(message: Message):
    if not message.caption:
        await message.answer("⚠️ Iltimos, PDF yuborayotganda izohga kitob nomini yozing!")
        return

    book_name = message.caption.strip()
    file_id = message.document.file_id

    BOOKS_DATABASE[book_name.lower()] = {
        "title": book_name,
        "file_id": file_id
    }
    save_data(DB_FILE, BOOKS_DATABASE)
    await message.answer(f"✅ **Kitob saqlandi:** {book_name}")

# Admin uchun foydalanuvchi balansini to'ldirish buyrug'i: /add ID SUMMA
@dp.message(Command("add"), F.from_user.id == ADMIN_ID)
async def add_balance_cmd(message: Message):
    try:
        args = message.text.split()
        target_id = str(args[1])
        amount = int(args[2])

        if target_id in USERS_DATABASE:
            USERS_DATABASE[target_id]["balance"] += amount
            save_data(USERS_FILE, USERS_DATABASE)

            await message.answer(f"✅ **ID `{target_id}` hisobi {amount:,} so'mga to'ldirildi!**\nYangi balans: {USERS_DATABASE[target_id]['balance']:,} so'm", parse_mode="Markdown")

            # Foydalanuvchiga xabar yuborish
            try:
                await bot.send_message(
                    chat_id=int(target_id),
                    text=f"🎉 **Hisobingiz to'ldirildi!**\n\n➕ **Qo'shildi:** {amount:,} so'm\n💰 **Jami balansingiz:** {USERS_DATABASE[target_id]['balance']:,} so'm",
                    parse_mode="Markdown"
                )
            except Exception as e:
                await message.answer(f"⚠️ Foydalanuvchiga xabar boramadi: {e}")
        else:
            await message.answer("❌ Boshqa bunday foydalanuvchi ID si topilmadi.")
    except Exception:
        await message.answer("⚠️ Notog'ri format! Ishlatish: `/add ID SUMMA`\nMasalan: `/add 1774408231 50000`", parse_mode="Markdown")

# -------------------------------------------------------------------
# 4. BOT RO'YXATDAN O'TISH KODLARI
# -------------------------------------------------------------------
@dp.message(CommandStart())
async def start_cmd(message: Message, state: FSMContext):
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🇺🇿 O'zbek")]],
        resize_keyboard=True
    )
    await message.answer("Tilni tanlang:", reply_markup=kb)
    await state.set_state(UserRegistration.language)

@dp.message(UserRegistration.language)
async def process_language(message: Message, state: FSMContext):
    await state.update_data(lang='uz')
    await message.answer(TEXTS['uz']['enter_fullname'], reply_markup=ReplyKeyboardRemove())
    await state.set_state(UserRegistration.fullname)

@dp.message(UserRegistration.fullname)
async def process_fullname(message: Message, state: FSMContext):
    await state.update_data(fullname=message.text.strip())

    regions_list = list(REGIONS.keys())
    keyboard = []
    for i in range(0, len(regions_list), 2):
        row = [KeyboardButton(text=regions_list[i])]
        if i + 1 < len(regions_list):
            row.append(KeyboardButton(text=regions_list[i + 1]))
        keyboard.append(row)

    kb = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    await message.answer(TEXTS['uz']['choose_region'], reply_markup=kb)
    await state.set_state(UserRegistration.region)

@dp.message(UserRegistration.region)
async def process_region(message: Message, state: FSMContext):
    region_name = message.text
    if region_name not in REGIONS:
        await message.answer(TEXTS['uz']['choose_region'])
        return

    await state.update_data(region=region_name)
    districts = REGIONS[region_name]

    keyboard = []
    for i in range(0, len(districts), 2):
        row = [KeyboardButton(text=districts[i])]
        if i + 1 < len(districts):
            row.append(KeyboardButton(text=districts[i + 1]))
        keyboard.append(row)

    kb = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    await message.answer(TEXTS['uz']['choose_district'], reply_markup=kb)
    await state.set_state(UserRegistration.district)

@dp.message(UserRegistration.district)
async def process_district(message: Message, state: FSMContext):
    await state.update_data(district=message.text)
    await message.answer(TEXTS['uz']['enter_mahalla'], reply_markup=ReplyKeyboardRemove())
    await state.set_state(UserRegistration.mahalla)

@dp.message(UserRegistration.mahalla)
async def process_mahalla(message: Message, state: FSMContext):
    await state.update_data(mahalla=message.text)
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=TEXTS['uz']['phone_btn'], request_contact=True)]],
        resize_keyboard=True
    )
    await message.answer(TEXTS['uz']['send_phone'], reply_markup=kb)
    await state.set_state(UserRegistration.phone)

@dp.message(UserRegistration.phone, F.contact)
async def process_phone(message: Message, state: FSMContext):
    phone = message.contact.phone_number
    await state.update_data(phone=phone)
    
    user_data = await state.get_data()
    user_id = str(message.from_user.id)
    
    tg_full_name = message.from_user.full_name 
    username = f"@{message.from_user.username}" if message.from_user.username else "Mavjud emas"
    input_fullname = user_data.get('fullname', 'Kiritilmagan')
    region = user_data.get('region', 'Ko\'rsatilmagan')
    district = user_data.get('district', 'Ko\'rsatilmagan')
    mahalla = user_data.get('mahalla', 'Ko\'rsatilmagan')

    USERS_DATABASE[user_id] = {
        "tg_name": tg_full_name,
        "input_fullname": input_fullname,
        "username": username,
        "phone": phone,
        "region": region,
        "district": district,
        "mahalla": mahalla,
        "balance": 0
    }
    save_data(USERS_FILE, USERS_DATABASE)

    admin_msg = (
        f"🔔 **Yangi foydalanuvchi ro'yxatdan o'tdi!**\n\n"
        f"👤 **Telegram Ismi:** {tg_full_name}\n"
        f"📝 **F.I.O (Kiritgan):** {input_fullname}\n"
        f"🔗 **Username:** {username}\n"
        f"🆔 **ID:** `{user_id}`\n"
        f"📱 **Tel:** `{phone}`\n"
        f"📍 **Manzil:** {region}, {district}, {mahalla}"
    )

    try:
        await bot.send_message(chat_id=ADMIN_ID, text=admin_msg, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Xatolik: {e}")

    await message.answer(TEXTS['uz']['main_menu'], reply_markup=main_keyboard())
    await state.set_state(UserRegistration.main_menu)

# -------------------------------------------------------------------
# 5. ALOHIDA MENYULAR: HISOBIM, BALANS, TO'LOV
# -------------------------------------------------------------------
@dp.message(F.text == "👤 Hisobim")
async def show_account(message: Message):
    user_id = str(message.from_user.id)
    user_info = USERS_DATABASE.get(user_id, {})
    
    tg_name = message.from_user.full_name
    input_fullname = user_info.get("input_fullname", "Kiritilmagan")
    phone = user_info.get("phone", "Yo'q")
    region = user_info.get("region", "Yo'q")
    district = user_info.get("district", "Yo'q")
    mahalla = user_info.get("mahalla", "Yo'q")
    balance = user_info.get("balance", 0)

    text = (
        f"📋 **SHAXSIY MA'LUMOTLARINGIZ:**\n\n"
        f"👤 **Telegram profildagi ism:** {tg_name}\n"
        f"📝 **To'liq F.I.O:** {input_fullname}\n"
        f"🆔 **Sizning ID:** `{user_id}`\n"
        f"📱 **Telefon:** {phone}\n"
        f"📍 **Manzil:** {region}, {district}, {mahalla} MFY\n\n"
        f"💰 **Joriy balansingiz:** `{balance:,}` so'm"
    )
    await message.answer(text, parse_mode="Markdown")

@dp.message(F.text == "💰 Balans")
async def show_balance(message: Message):
    user_id = str(message.from_user.id)
    user_info = USERS_DATABASE.get(user_id, {})
    balance = user_info.get("balance", 0)

    text = (
        f"💰 **BALANS BILDIRISHNOMASI:**\n\n"
        f"Hozirgi hisobingizdagi mablag': **{balance:,} so'm**\n\n"
        "Hisobni to'ldirish uchun quyidagi **💳 To'lov qilish** tugmasidan foydalaning."
    )
    await message.answer(text, parse_mode="Markdown")

@dp.message(F.text == "💳 To'lov qilish")
async def process_payment_option(message: Message):
    text = (
        "💳 **To'lov usulini tanlang:**\n\n"
        "Hisobingizni to'ldirish uchun kerakli to'lov tizimini bosing:"
    )
    
    payment_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔹 Click orqali to'lash", callback_query_data="pay_click")],
            [InlineKeyboardButton(text="🔹 Payme orqali to'lash", callback_query_data="pay_payme")]
        ]
    )
    await message.answer(text, reply_markup=payment_kb, parse_mode="Markdown")

@dp.callback_query(F.data.in_(["pay_click", "pay_payme"]))
async def payment_info(callback: CallbackQuery):
    await callback.answer()
    system = "Click" if callback.data == "pay_click" else "Payme"
    text = (
        f"💳 **{system} orqali to'lov qilish:**\n\n"
        f"Karta raqam: `{CARD_NUMBER}`\n"
        f"Qabul qiluvchi: Bot Admini\n\n"
        "⚠️ **Eslatma:** To'lovni amalga oshirgach, **to'lov chekini (rasmini) ushbu botga yuboring.** Admin chekni tekshirib, balansingizni to'ldiradi."
    )
    await callback.message.answer(text, parse_mode="Markdown")

# FOYDALANUVCHIDAN TO'LOV CHEKI (RASM) KELGANDA ADMINGA YUBORISH
@dp.message(F.photo)
async def forward_receipt(message: Message):
    user_id = message.from_user.id
    tg_name = message.from_user.full_name

    caption = (
        f"📸 **Yangi To'lov Cheki Keldi!**\n\n"
        f"👤 Foydalanuvchi: {tg_name}\n"
        f"🆔 ID: `{user_id}`\n\n"
        f" Balansni to'ldirish uchun adminga buyruq:\n"
        f"`/add {user_id} SUMMA`"
    )
    await bot.send_photo(chat_id=ADMIN_ID, photo=message.photo[-1].file_id, caption=caption, parse_mode="Markdown")
    await message.answer("✅ **To'lov chekingiz adminga yuborildi!**\nTez orada chek tekshirilib, balansingiz to'ldiriladi.")

# -------------------------------------------------------------------
# 6. KITOB QIDIRISH
# -------------------------------------------------------------------
@dp.message(UserRegistration.main_menu)
async def search_book(message: Message, state: FSMContext):
    if message.text in ["👤 Hisobim", "💰 Balans", "💳 To'lov qilish"]:
        return

    query = message.text.strip().lower()
    found_book = None
    for key, book_info in BOOKS_DATABASE.items():
        if key in query or query in key:
            found_book = book_info
            break

    if found_book:
        await message.answer(TEXTS['uz']['sending_book'])
        try:
            await message.answer_document(
                document=found_book['file_id'],
                caption=f"📚 {found_book['title']}"
            )
        except Exception as e:
            await message.answer(f"Xatolik yuz berdi: {str(e)}")
    else:
        await message.answer(TEXTS['uz']['book_not_found'])

# -------------------------------------------------------------------
# 7. ISHGA TUSHIRISH
# -------------------------------------------------------------------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
