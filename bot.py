import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

load_dotenv()

logging.basicConfig(level=logging.INFO)
bot = Bot(token=os.getenv("8776710990:AAGug1MWNSEumJ40w3xdjDQZmpZkvra-f2M"))
dp = Dispatcher()

# ─── /start ───────────────────────────
@dp.message(Command("start"))
async def start(message: types.Message):
    user = message.from_user
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔵 Matematika", callback_data="cat_math"),
         InlineKeyboardButton(text="🟢 Geometriya", callback_data="cat_geo")],
        [InlineKeyboardButton(text="🔴 Fizika", callback_data="cat_phys")],
        [InlineKeyboardButton(text="🎲 Tasodifiy formula", callback_data="random")],
        [InlineKeyboardButton(text="🔍 Qidirish", switch_inline_query_current_chat="")]
    ])
    
    await message.answer(
        f"✨ <b>Assalomu alaykum, {user.first_name}!</b>\n\n"
        f"📚 <b>AuraSTEM</b> — 120 ta mukammal formula\n"
        f"🇺🇿 O‘zbek tilidagi eng kuchli STEM platformasi\n\n"
        f"📌 Kerakli bo‘limni tanlang:",
        parse_mode="HTML",
        reply_markup=keyboard
    )

# ─── /help ────────────────────────────
@dp.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer(
        "📖 <b>Yordam</b>\n\n"
        "🔹 /start — Bosh menyu\n"
        "🔹 /random — Tasodifiy formula\n"
        "🔹 /help — Yordam\n\n"
        "💡 Tez orada qidiruv va testlar qo‘shiladi!",
        parse_mode="HTML"
    )

# ─── /random ──────────────────────────
@dp.message(Command("random"))
async def random_command(message: types.Message):
    await message.answer(
        "🎲 <b>Tasodifiy formula</b>\n\n"
        "📌 Kvadrat tenglama formulasi\n"
        "📝 $$x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$\n\n"
        "🔢 Tez orada 120 ta formula biriktiriladi!",
        parse_mode="HTML"
    )

# ─── Kategoriya tugmalarini qaytarish ──
@dp.callback_query(lambda c: c.data == "cat_math")
async def cat_math(callback: types.CallbackQuery):
    await callback.message.answer("🔵 <b>Matematika</b> — Tez orada 82 ta formula!", parse_mode="HTML")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "cat_geo")
async def cat_geo(callback: types.CallbackQuery):
    await callback.message.answer("🟢 <b>Geometriya</b> — Tez orada 58 ta formula!", parse_mode="HTML")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "cat_phys")
async def cat_phys(callback: types.CallbackQuery):
    await callback.message.answer("🔴 <b>Fizika</b> — Tez orada 38 ta formula!", parse_mode="HTML")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "random")
async def btn_random(callback: types.CallbackQuery):
    await callback.message.answer("🎲 <b>Tasodifiy formula</b> — Tez orada!", parse_mode="HTML")
    await callback.answer()

# ─── Render uchun web server (uxlamaslik uchun) ──
async def handle(request):
    return web.Response(text="AuraSTEM bot ishlayapti!")

async def main():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 8000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    print(f"🤖 AuraSTEM bot ishga tushdi! Port: {port}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
