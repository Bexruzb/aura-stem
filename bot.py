import asyncio
import logging
import os
import json
import random as rnd
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

load_dotenv()

logging.basicConfig(level=logging.INFO)
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

# ─── FORMULALARNI YUKLASH ──────────────
with open("formulas.json", "r", encoding="utf-8") as f:
    FORMULAS = json.load(f)

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
        f"🇺🇿 O‘zbek tilidagi eng kuchli STEM platformasi\n"
        f"👨‍💻 Muallif: <b>Yoldoshev</b>\n\n"
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
        "🔹 /search formula — Formula qidirish\n"
        "🔹 /random — Tasodifiy formula\n"
        "🔹 /stats — Statistika\n"
        "🔹 /help — Yordam\n\n"
        "👨‍💻 Muallif: @yoldoshev_2\n"
        "📢 Kanal: @aurastem",
        parse_mode="HTML"
    )

# ─── /random ──────────────────────────
@dp.message(Command("random"))
async def random_command(message: types.Message):
    f = rnd.choice(FORMULAS)
    await message.answer(format_formula(f), parse_mode="HTML")

# ─── /search ──────────────────────────
@dp.message(Command("search"))
async def search_command(message: types.Message):
    query = message.text.replace("/search", "").strip()
    if not query:
        await message.answer("🔍 <b>Iltimos, kalit so‘z kiriting:</b> /search Nyuton", parse_mode="HTML")
        return
    
    results = [f for f in FORMULAS if 
               query.lower() in f["title"].lower() or 
               query.lower() in f["label"].lower() or
               any(query.lower() in tag.lower() for tag in f.get("tags", []))]
    
    if not results:
        await message.answer("❌ Hech narsa topilmadi.", parse_mode="HTML")
        return
    
    await message.answer(f"🔍 <b>{len(results)} ta natija topildi:</b>", parse_mode="HTML")
    for f in results[:10]:
        await message.answer(format_formula(f), parse_mode="HTML")

# ─── /stats ──────────────────────────
@dp.message(Command("stats"))
async def stats_command(message: types.Message):
    math = len([f for f in FORMULAS if f["cat"] == "math"])
    geo = len([f for f in FORMULAS if f["cat"] == "geo"])
    phys = len([f for f in FORMULAS if f["cat"] == "phys"])
    
    await message.answer(
        f"📊 <b>AuraSTEM Statistika</b>\n\n"
        f"🔵 Matematika: <b>{math} ta</b>\n"
        f"🟢 Geometriya: <b>{geo} ta</b>\n"
        f"🔴 Fizika: <b>{phys} ta</b>\n\n"
        f"📚 <b>Jami: {len(FORMULAS)} ta formula</b>\n\n"
        f"👨‍💻 Muallif: @yoldoshev_2",
        parse_mode="HTML"
    )

# ─── kategoriya tugmalari ─────────────
@dp.callback_query(lambda c: c.data == "cat_math")
async def cat_math(callback: types.CallbackQuery):
    formulas = [f for f in FORMULAS if f["cat"] == "math"]
    await callback.message.answer(
        f"🔵 <b>Matematika — {len(formulas)} ta formula</b>\n\n"
        f"📌 Qidirish uchun: /search kalit",
        parse_mode="HTML"
    )
    for f in formulas[:5]:
        await callback.message.answer(format_formula(f), parse_mode="HTML")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "cat_geo")
async def cat_geo(callback: types.CallbackQuery):
    formulas = [f for f in FORMULAS if f["cat"] == "geo"]
    await callback.message.answer(
        f"🟢 <b>Geometriya — {len(formulas)} ta formula</b>\n\n"
        f"📌 Qidirish uchun: /search kalit",
        parse_mode="HTML"
    )
    for f in formulas[:5]:
        await callback.message.answer(format_formula(f), parse_mode="HTML")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "cat_phys")
async def cat_phys(callback: types.CallbackQuery):
    formulas = [f for f in FORMULAS if f["cat"] == "phys"]
    await callback.message.answer(
        f"🔴 <b>Fizika — {len(formulas)} ta formula</b>\n\n"
        f"📌 Qidirish uchun: /search kalit",
        parse_mode="HTML"
    )
    for f in formulas[:5]:
        await callback.message.answer(format_formula(f), parse_mode="HTML")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "random")
async def btn_random(callback: types.CallbackQuery):
    f = rnd.choice(FORMULAS)
    await callback.message.answer(format_formula(f), parse_mode="HTML")
    await callback.answer()

# ─── formula formatlash ──────────────
def format_formula(f):
    cat_emoji = {"math": "🔵", "geo": "🟢", "phys": "🔴"}
    emoji = cat_emoji.get(f["cat"], "📌")
    
    return (
        f"{emoji} <b>#{f['id']} {f['title']}</b>\n"
        f"🏷 {f['label']}\n"
        f"🏷 {', '.join(f.get('tags', []))}\n\n"
        f"📝 <code>{f['formula']}</code>\n\n"
        f"🔗 Batafsil: @aura_stembot"
    )

# ─── Render web server ──────────────
async def handle(request):
    return web.Response(text="AuraSTEM bot is working!\n@yoldoshev_2")

async def main():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 8000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    print(f"🤖 AuraSTEM bot ishga tushdi! {len(FORMULAS)} ta formula yuklandi.")
    print(f"👨‍💻 Muallif: @yoldoshev_2")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
