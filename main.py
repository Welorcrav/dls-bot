import asyncio
import logging
import firebase_admin
from firebase_admin import credentials, firestore

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)

# ==================== SOZLAMALAR ====================
BOT_TOKEN = "8990263071:AAHH2B5b-7rwVVctB7jHtkuzII1mrymDAPI"
ADMIN_ID = 8278723918

# 1. FIREBASE DASTURINI ISHGA TUSHRISH
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# ==================== FIREBASE FUNKSIYALARI ====================
def add_user(user_id: int):
    doc_ref = db.collection("users").document(str(user_id))
    if not doc_ref.get().exists:
        doc_ref.set({"user_id": user_id})

def get_users():
    users_ref = db.collection("users").stream()
    return [int(user.id) for user in users_ref]

def get_content(button_key: str):
    doc_ref = db.collection("buttons").document(button_key)
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        return data.get("photo_id"), data.get("text")
    else:
        default_texts = {
            "btn_turnir": "SHU TURNIRGA QATNASHISH UCHUN @DLSRASMIY_UZ\n@DLSTEKINAKLARI\n@DLS_UZBBB KANALLARIGA OBUNA BOLING VA @dlschi_oka ga screen tashlang va turnir ishtirokchisi boling✅",
            "btn_vietnam": "SIZ TEKINGA @dlschi_oka orqali vietnamdan akk kerakmi TEKINGA unda siz @DLSTEKINAKLARI KANALIDA AKTIV BOLING BOT 24 soat ichida sizga akk kodini tashlaydi 💬",
            "btn_guruh": "@dls2026gruppasi\n@DLSGRUPPASI2026\n\nBizning shu guruhlarimizga odam qo'shib akk yutib olsa boladi siz 40 tadan kop odam qoshasiz va botga screen yuborasiz bot sizga 24 soat ichida akk kodini beradi",
            "btn_tekin": "BIZDA SHUNAQA AKKLAR BOR ULARNI BIZ VIETNAMDAN OLAMIZ BUNAQA AKKLARNI TEKINGA AKTIV OBUNACHILARIMIZGA BERAMIZ ✅\n\n@DLSTEKINAKLARI\n@DLSRASMIY_UZ\n@DLS_UZBBB KANALLARIGA OBUNA BOLING VA TEKINGA AKKAUNT YUTIB OLING 🚫"
        }
        txt = default_texts.get(button_key, "Ma'lumot topilmadi.")
        return None, txt

def update_content(button_key: str, photo_id: str, text: str):
    db.collection("buttons").document(button_key).set({
        "photo_id": photo_id,
        "text": text
    })

# ==================== BOT SETUP ====================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class AdminStates(StatesGroup):
    waiting_for_content = State()
    waiting_for_broadcast = State()

def get_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="TURNIRGA QATNASHISH")],
            [KeyboardButton(text="DLS VIETNAM AKK OLISH 🔐")],
            [KeyboardButton(text="GURUHGA ODAM QOSHIB AKK OLISH ❤️‍🔥")],
            [KeyboardButton(text="DLS TEKIN AKK OLISH ✅")]
        ],
        resize_keyboard=True
    )

def get_admin_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⚙️ Tugmalar kontentini o'zgartirish", callback_data="admin_edit_buttons")],
            [InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats")],
            [InlineKeyboardButton(text="📢 Xabar tarqatish (Broadcast)", callback_data="admin_broadcast")]
        ]
    )

# ==================== HANDLERLAR ====================
@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    add_user(message.from_user.id)
    text = (
        "TEKIN AKK OLISH UCHUN @DLSTEKINAKLARI KANALIGA OBUNA BOLING\n\n"
        "ASSALOMU ALEYKUM\n"
        "SIZ BEHRUZ NING BOTIDASIZ /start ORQALI BARCHA XIZMATLARDAN FOYDALANISHIZ MUMKIN"
    )
    await message.answer(text, reply_markup=get_main_menu())

async def send_button_response(message: types.Message, button_key: str):
    photo_id, text = get_content(button_key)
    if photo_id:
        await message.answer_photo(photo=photo_id, caption=text)
    else:
        await message.answer(text)

@dp.message(F.text == "TURNIRGA QATNASHISH")
async def turnir_handler(message: types.Message):
    await send_button_response(message, "btn_turnir")

@dp.message(F.text == "DLS VIETNAM AKK OLISH 🔐")
async def vietnam_handler(message: types.Message):
    await send_button_response(message, "btn_vietnam")

@dp.message(F.text == "GURUHGA ODAM QOSHIB AKK OLISH ❤️‍🔥")
async def guruh_handler(message: types.Message):
    await send_button_response(message, "btn_guruh")

@dp.message(F.text == "DLS TEKIN AKK OLISH ✅")
async def tekin_handler(message: types.Message):
    await send_button_response(message, "btn_tekin")

# ==================== ADMIN PANEL ====================
@dp.message(Command("admin"))
async def admin_cmd(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    await message.answer("👑 **Admin Panelga xush kelibsiz!**", reply_markup=get_admin_menu(), parse_mode="Markdown")

@dp.callback_query(F.data == "admin_stats")
async def admin_stats(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID: return
    users = get_users()
    await call.message.answer(f"📊 **Firebase Statistika:**\nJami foydalanuvchilar: **{len(users)}** ta", parse_mode="Markdown")
    await call.answer()

@dp.callback_query(F.data == "admin_edit_buttons")
async def admin_edit_buttons(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID: return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1. TURNIRGA QATNASHISH", callback_data="edit_btn_turnir")],
        [InlineKeyboardButton(text="2. DLS VIETNAM AKK OLISH", callback_data="edit_btn_vietnam")],
        [InlineKeyboardButton(text="3. GURUHGA ODAM QOSHIB AKK OLISH", callback_data="edit_btn_guruh")],
        [InlineKeyboardButton(text="4. DLS TEKIN AKK OLISH", callback_data="edit_btn_tekin")]
    ])
    await call.message.answer("✏️ Qaysi tugmani Firebase'da o'zgartirmoqchisiz?", reply_markup=kb)
    await call.answer()

@dp.callback_query(F.data.startswith("edit_"))
async def process_button_edit_select(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID: return
    btn_key = call.data.replace("edit_", "")
    await state.update_data(selected_button=btn_key)
    await call.message.answer("📸 Yangi post yuboring (Rasm va matn yoki faqat matn).\n\n_Bekor qilish: /cancel_", parse_mode="Markdown")
    await state.set_state(AdminStates.waiting_for_content)
    await call.answer()

@dp.message(AdminStates.waiting_for_content)
async def save_button_content(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    if message.text == "/cancel":
        await state.clear()
        return await message.answer("❌ Bekor qilindi.")

    data = await state.get_data()
    btn_key = data.get("selected_button")

    photo_id = message.photo[-1].file_id if message.photo else None
    text = message.caption if message.photo else message.text

    update_content(btn_key, photo_id, text)
    await state.clear()
    await message.answer("✅ **Firebase'da muvaffaqiyatli saqlandi!**", parse_mode="Markdown")

@dp.callback_query(F.data == "admin_broadcast")
async def start_broadcast(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID: return
    await call.message.answer("📢 Tarqatiladigan xabarni yuboring:\n\n_Bekor qilish: /cancel_", parse_mode="Markdown")
    await state.set_state(AdminStates.waiting_for_broadcast)
    await call.answer()

@dp.message(AdminStates.waiting_for_broadcast)
async def process_broadcast(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    if message.text == "/cancel":
        await state.clear()
        return await message.answer("❌ Bekor qilindi.")

    users = get_users()
    count = 0
    await message.answer("⏳ Broadcast ketmoqda...")

    for uid in users:
        try:
            await message.copy_to(chat_id=uid)
            count += 1
            await asyncio.sleep(0.05)
        except Exception:
            pass

    await state.clear()
    await message.answer(f"✅ Xabar **{count}** ta foydalanuvchiga yuborildi!")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())