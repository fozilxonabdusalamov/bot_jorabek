import asyncio
import logging
import sys
import html
import os
from dotenv import load_dotenv

from aiogram import Dispatcher, types
from aiogram.client.bot import Bot, DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

# .env faylini yuklash
load_dotenv()

# TOKEN va ADMIN_CHANNEL ni .env dan olish
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHANNEL_ID_STR = os.getenv("ADMIN_CHANNEL")

if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set or missing in .env file")
if not ADMIN_CHANNEL_ID_STR:
    raise ValueError("ADMIN_CHANNEL environment variable not set or missing in .env file")

ADMIN_CHANNEL = int(ADMIN_CHANNEL_ID_STR)

# --- FSM HOLATLARI ---
class Form(StatesGroup):
    firstname = State()
    lastname = State()
    age = State()
    level = State()
    teachername = State()
    number = State()
    familynumber = State()

# --- CANCEL TUGMASI ---
cancel_btn = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌ Bekor qilish")]],
    resize_keyboard=True
)

dp = Dispatcher(storage=MemoryStorage())

# --- /start ---
@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer(
        "Ro'yxatdan o'tish boshlandi! 👇\n\nIltimos, ismingizni kiriting:",
        reply_markup=cancel_btn
    )
    await state.set_state(Form.firstname)

# --- FSM HANDLERLARI ---
@dp.message(Form.firstname)
async def process_firstname(message: types.Message, state: FSMContext):
    await state.update_data(firstname=message.text)
    await message.answer("Familyangizni kiriting:")
    await state.set_state(Form.lastname)

@dp.message(Form.lastname)
async def process_lastname(message: types.Message, state: FSMContext):
    await state.update_data(lastname=message.text)
    await message.answer("Yoshingizni kiriting:")
    await state.set_state(Form.age)

@dp.message(Form.age)
async def process_age(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("Darajangizni kiriting:")
    await state.set_state(Form.level)

@dp.message(Form.level)
async def process_level(message: types.Message, state: FSMContext):
    await state.update_data(level=message.text)
    await message.answer("Ustozingiz ismini kiriting:")
    await state.set_state(Form.teachername)

@dp.message(Form.teachername)
async def process_teachername(message: types.Message, state: FSMContext):
    await state.update_data(teachername=message.text)
    await message.answer("Telefon raqamingizni kiriting:")
    await state.set_state(Form.number)

@dp.message(Form.number)
async def process_number(message: types.Message, state: FSMContext):
    await state.update_data(number=message.text)
    await message.answer("Ota-onangiz telefon raqamini kiriting:")
    await state.set_state(Form.familynumber)

@dp.message(Form.familynumber)
async def process_familynumber(message: types.Message, state: FSMContext, bot: Bot):
    await state.update_data(familynumber=message.text)
    data = await state.get_data()

    text = (
        f"👤 Ism: <b>{html.escape(data.get('firstname'))}</b>\n"
        f"👪 Familya: <b>{html.escape(data.get('lastname'))}</b>\n"
        f"🎂 Yosh: <b>{html.escape(data.get('age'))}</b>\n"
        f"🎓 Daraja: <b>{html.escape(data.get('level'))}</b>\n"
        f"👨‍🏫 Ustoz: <b>{html.escape(data.get('teachername'))}</b>\n"
        f"📞 Tel: <b>{html.escape(data.get('number'))}</b>\n"
        f"📱 Ota-ona tel: <b>{html.escape(data.get('familynumber'))}</b>"
    )

    await message.answer(
        "Ma'lumot kiritganingiz uchun rahmat! 😊\n\n" + text,
        reply_markup=ReplyKeyboardRemove()
    )

    await bot.send_message(ADMIN_CHANNEL, text)
    await state.clear()

# --- CANCEL HANDLER ---
@dp.message(lambda message: message.text == "❌ Bekor qilish")
async def cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❌ Jarayon bekor qilindi.",
        reply_markup=ReplyKeyboardRemove()
    )

# --- BOTNI ISHGA TUSHIRISH ---
async def main() -> None:
    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
