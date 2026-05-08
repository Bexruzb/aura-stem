import asyncio
import logging
import os
import json
import random as rnd
import datetime
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    InlineQuery, InlineQueryResultArticle,
    InputTextMessageContent
)
from aiohttp import web
import aiosqlite

load_dotenv()

logging.basicConfig(level=logging.INFO)
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

# ─── FORMULALARNI YUKLASH ──────────────
with open("formulas.json", "r", encoding="utf-8") as f:
    FORMULAS = json.load(f)

# ─── DATABASE ──────────────────────────
async def init_db():
    async with aiosqlite.connect("aurastem.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                score INTEGER DEFAULT 0,
                formulas_viewed INTEGER DEFAULT 0
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS bookmarks (
                user_id INTEGER,
                formula_id INTEGER,
                PRIMARY KEY (user_id, formula_id)
            )
        """)
        await db.commit()

async def update_user(user_id, username, first_name):
    async with aiosqlite.connect("aurastem.db") as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)",
            (user_id, username, first_name)
        )
        await db.execute(
            "UPDATE users SET formulas_viewed = formulas_viewed + 1 WHERE user_id = ?",
            (user_id,)
        )
        await db.commit()

async def add_score(user_id, points):
    async with aiosqlite.connect("aurastem.db") as db:
        await db.execute(
            "UPDATE users SET score = score + ? WHERE user_id = ?",
            (points, user_id)
        )
        await db.commit()

async def get_leaderboard(limit=10):
    async with aiosqlite.connect("aurastem.db") as db:
        cursor = await db.execute(
            "SELECT username, first_name, score, formulas_viewed FROM users ORDER BY score DESC LIMIT ?",
            (limit,)
        )
        return await cursor.fetchall()

async def get_user_stats(user_id):
    async with aiosqlite.connect("aurastem.db") as db:
        cursor = await db.execute(
            "SELECT score, formulas_viewed FROM users WHERE user_id = ?",
            (user_id,)
        )
        return await cursor.fetchone()

# ─── FORMATLASH ────────────────────────
def format_formula(f):
    cat_emoji = {"math": "🔵", "geo": "🟢", "phys": "🔴"}
    emoji = cat_emoji.get(f["cat"], "📌")
    
    return (
        f"{emoji} <b>#{f['id']} {f['title']}</b>\n"
        f"🏷 {f['label']}\n"
        f"🏷 {' • '.join(f.get('tags', []))}\n\n"
        f"📝 <code>{f['formula']}</code>\n\n"
        f"👨‍💻 @yoldoshev_2 | @aurastem"
    )

def format_formula_long(f):
    cat_emoji = {"math": "🔵", "geo": "🟢", "phys": "🔴"}
    emoji = cat_emoji.get(f["cat"], "📌")
    
    return (
        f"{emoji} <b>#{f['id']} {f['title']}</b>\n\n"
        f"📚 <b>Kategoriya:</b> {f['label']}\n"
        f"🏷 <b>Teglar:</b> {' • '.join(f.get('tags', []))}\n\n"
        f"📝 <b>Formula:</b>\n<code>{f['formula']}</code>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👨‍💻 Muallif: @yoldoshev_2\n"
        f"📢 Kanal: @aurastem\n"
        f"🤖 Bot: @aura_stembot"
    )

# ─── /start ───────────────────────────
@dp.message(Command("start"))
async def start(message: types.Message):
    user = message.from_user
    await update_user(user.id, user.username, user.first_name)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔵 Matematika", callback_data="cat_math"),
         InlineKeyboardButton(text="🟢 Geometriya", callback_data="cat_geo")],
        [InlineKeyboardButton(text="🔴 Fizika", callback_data="cat_phys")],
        [InlineKeyboardButton(text="🎲 Tasodifiy", callback_data="random"),
         InlineKeyboardButton(text="🎰 Ruletka", callback_data="spin")],
        [InlineKeyboardButton(text="🧠 Test", callback_data="quiz_start"),
         InlineKeyboardButton(text="⚔️ Bellashuv", callback_data="challenge_start")],
        [InlineKeyboardButton(text="🏆 Reyting", callback_data="leaderboard"),
         InlineKeyboardButton(text="📊 Hisobot", callback_data="weekly")],
        [InlineKeyboardButton(text="🔍 Inline qidiruv", switch_inline_query_current_chat="")]
    ])
    
    await message.answer(
        f"✨ <b>Assalomu alaykum, {user.first_name}!</b>\n\n"
        f"📚 <b>AuraSTEM</b> — 120 ta mukammal formula\n"
        f"🇺🇿 O‘zbek tilidagi eng kuchli STEM platformasi\n"
        f"👨‍💻 Muallif: <b>Yoldoshev</b>\n\n"
        f"🎮 <b>Yangi o‘yinlar:</b>\n"
        f"• 🧠 Formula testi — /quiz\n"
        f"• 🎰 Formula ruletkasi — /spin\n"
        f"• ⚔️ Do‘stlar bilan bellashuv — /challenge\n"
        f"• 📊 Haftalik hisobot — /weekly\n"
        f"• 💬 Inline: @aura_stembot formula\n\n"
        f"📌 Tanlang:",
        parse_mode="HTML",
        reply_markup=keyboard
    )

# ─── /help ────────────────────────────
@dp.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer(
        "📖 <b>Yordam</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🔹 /start — Bosh menyu\n"
        "🔹 /search formula — Formula qidirish\n"
        "🔹 /random — Tasodifiy formula\n"
        "🔹 /quiz — Formula testi\n"
        "🔹 /spin — Formula ruletkasi\n"
        "🔹 /challenge — Do‘st bilan bellashuv\n"
        "🔹 /daily — Kunlik challenge\n"
        "🔹 /leaderboard — Reyting\n"
        "🔹 /weekly — Haftalik hisobot\n"
        "🔹 /stats — Statistika\n"
        "🔹 /bookmark ID — Xatcho‘pga qo‘shish\n"
        "🔹 /help — Yordam\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🪄 <b>Maxsus funksiyalar:</b>\n\n"
        "💬 <b>Inline:</b> @aura_stembot kalit\n"
        "🎙 <b>Ovozli:</b> ovozli xabar yuboring\n\n"
        "👨‍💻 Muallif: @yoldoshev_2\n"
        "📢 Kanal: @aurastem",
        parse_mode="HTML"
    )

# ─── /random ──────────────────────────
@dp.message(Command("random"))
async def random_command(message: types.Message):
    user = message.from_user
    await update_user(user.id, user.username, user.first_name)
    f = rnd.choice(FORMULAS)
    await message.answer(format_formula_long(f), parse_mode="HTML")
    await add_score(user.id, 3)

# ─── /search ──────────────────────────
@dp.message(Command("search"))
async def search_command(message: types.Message):
    user = message.from_user
    await update_user(user.id, user.username, user.first_name)
    
    query = message.text.replace("/search", "").strip()
    if not query:
        await message.answer("🔍 <b>Iltimos, kalit so‘z kiriting:</b>\n/search Nyuton", parse_mode="HTML")
        return
    
    results = [f for f in FORMULAS if 
               query.lower() in f["title"].lower() or 
               query.lower() in f["label"].lower() or
               any(query.lower() in tag.lower() for tag in f.get("tags", []))]
    
    if not results:
        await message.answer("❌ Hech narsa topilmadi.", parse_mode="HTML")
        return
    
    await message.answer(f"🔍 <b>{len(results)} ta natija topildi:</b>", parse_mode="HTML")
    for f in results[:5]:
        await message.answer(format_formula(f), parse_mode="HTML")

# ─── /quiz ─────────────────────────────
@dp.message(Command("quiz"))
async def quiz_command(message: types.Message):
    f = rnd.choice(FORMULAS)
    
    wrong_answers = rnd.sample([x for x in FORMULAS if x["id"] != f["id"]], 3)
    
    correct_pos = rnd.randint(0, 3)
    options = []
    for i in range(4):
        if i == correct_pos:
            options.append(f["title"][:50])
        else:
            idx = i if i < correct_pos else i-1
            options.append(wrong_answers[idx]["title"][:50])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"A) {options[0]}", callback_data=f"quiz_{f['id']}_0_{correct_pos}")],
        [InlineKeyboardButton(text=f"B) {options[1]}", callback_data=f"quiz_{f['id']}_1_{correct_pos}")],
        [InlineKeyboardButton(text=f"C) {options[2]}", callback_data=f"quiz_{f['id']}_2_{correct_pos}")],
        [InlineKeyboardButton(text=f"D) {options[3]}", callback_data=f"quiz_{f['id']}_3_{correct_pos}")],
    ])
    
    await message.answer(
        f"🧠 <b>TEST SAVOLI</b>\n\n"
        f"Quyidagi formula qanday nomlanadi?\n\n"
        f"📝 <code>{f['formula']}</code>\n\n"
        f"🏷 Kategoriya: {f['label']}",
        parse_mode="HTML",
        reply_markup=keyboard
    )

@dp.callback_query(lambda c: c.data.startswith("quiz_"))
async def quiz_answer(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    formula_id = int(parts[1])
    user_choice = int(parts[2])
    correct_pos = int(parts[3])
    
    f = next((x for x in FORMULAS if x["id"] == formula_id), None)
    
    if user_choice == correct_pos:
        await callback.message.answer(
            f"✅ <b>TO‘G‘RI!</b> 🎉 +15 ball\n\n{format_formula_long(f)}",
            parse_mode="HTML"
        )
        await add_score(callback.from_user.id, 15)
    else:
        await callback.message.answer(
            f"❌ <b>XATO!</b> 😢 +2 ball\n\nTo‘g‘ri javob:\n{format_formula_long(f)}",
            parse_mode="HTML"
        )
        await add_score(callback.from_user.id, 2)
    
    await callback.answer()

# ─── /spin ────────────────────────────
@dp.message(Command("spin"))
async def spin_command(message: types.Message):
    user = message.from_user
    await update_user(user.id, user.username, user.first_name)
    
    cat_emojis = [("🔵", "Matematika"), ("🟢", "Geometriya"), ("🔴", "Fizika")]
    emoji, cat_name = rnd.choice(cat_emojis)
    
    cat_map = {"Matematika": "math", "Geometriya": "geo", "Fizika": "phys"}
    formulas = [f for f in FORMULAS if f["cat"] == cat_map[cat_name]]
    f = rnd.choice(formulas)
    
    await message.answer(
        f"🎰 <b>FORMULA RULETKASI!</b>\n\n"
        f"Ruletka: {emoji} <b>{cat_name}</b> da to‘xtadi!\n\n"
        f"{format_formula_long(f)}",
        parse_mode="HTML"
    )
    await add_score(user.id, 5)

# ─── /challenge ────────────────────────
@dp.message(Command("challenge"))
async def challenge_command(message: types.Message):
    user = message.from_user
    score = rnd.randint(50, 200)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 Challenge qabul qilish!", callback_data=f"challenge_{user.id}_{score}")]
    ])
    
    await message.answer(
        f"⚔️ <b>{user.first_name}</b> sizni bellashuvga chorlaydi!\n\n"
        f"🏆 Yutuq: {score} ball\n\n"
        f"Qabul qilasizmi? 👇",
        parse_mode="HTML",
        reply_markup=keyboard
    )

@dp.callback_query(lambda c: c.data.startswith("challenge_") and not c.data.startswith("challenge_start"))
async def challenge_accept(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    challenger_id = int(parts[1])
    score = int(parts[2])
    
    await add_score(challenger_id, score)
    await add_score(callback.from_user.id, score)
    
    await callback.message.answer(
        f"⚔️ <b>Bellashuv qabul qilindi!</b>\n\n"
        f"Ikki o‘yinchi <b>+{score} ball</b> oldi! 🎉",
        parse_mode="HTML"
    )
    await callback.answer("🔥 Bellashuv!")

# ─── /daily ───────────────────────────
@dp.message(Command("daily"))
async def daily_command(message: types.Message):
    user = message.from_user
    daily_formulas = rnd.sample(FORMULAS, min(5, len(FORMULAS)))
    
    await message.answer(
        f"🏆 <b>Bugungi Challenge!</b>\n"
        f"📅 {datetime.date.today()}\n\n"
        f"5 ta formulani o‘rganing:\n\n"
        + "\n".join([f"• {f['title']}" for f in daily_formulas]) +
        f"\n\n⭐ +25 ball!",
        parse_mode="HTML"
    )
    
    for f in daily_formulas:
        await message.answer(format_formula_long(f), parse_mode="HTML")
    
    await add_score(user.id, 25)

# ─── /leaderboard ─────────────────────
@dp.message(Command("leaderboard"))
async def leaderboard_command(message: types.Message):
    top = await get_leaderboard(10)
    
    if not top:
        await message.answer("📊 Hali hech kim ball to‘plamagan!", parse_mode="HTML")
        return
    
    text = "🏆 <b>REYTING TOP-10</b>\n\n"
    medals = {0: "🥇", 1: "🥈", 2: "🥉"}
    
    for i, (username, first_name, score, viewed) in enumerate(top):
        medal = medals.get(i, f"{i+1}.")
        name = first_name or username or "Anonim"
        text += f"{medal} <b>{name}</b> — ⭐{score} ball | 👁{viewed} ta\n"
    
    text += f"\n👨‍💻 @yoldoshev_2"
    
    await message.answer(text, parse_mode="HTML")

# ─── /weekly ──────────────────────────
@dp.message(Command("weekly"))
async def weekly_command(message: types.Message):
    user = message.from_user
    stats = await get_user_stats(user.id)
    
    score = stats[0] if stats else 0
    viewed = stats[1] if stats else 0
    
    if score < 100:
        level = "🌱 Boshlang'ich"
    elif score < 300:
        level = "🌿 O‘rta"
    elif score < 600:
        level = "🌳 Yuqori"
    elif score < 1000:
        level = "🏆 Profi"
    else:
        level = "👑 Legend"
    
    await message.answer(
        f"📅 <b>HAFTALIK HISOBOT</b>\n\n"
        f"👤 {user.first_name}\n"
        f"📊 Daraja: <b>{level}</b>\n"
        f"⭐ Ball: <b>{score}</b>\n"
        f"👁 Ko‘rilgan: <b>{viewed} ta</b>\n\n"
        f"💪 Davom eting!",
        parse_mode="HTML"
    )

# ─── /stats ──────────────────────────
@dp.message(Command("stats"))
async def stats_command(message: types.Message):
    user = message.from_user
    user_stats = await get_user_stats(user.id)
    
    math = len([f for f in FORMULAS if f["cat"] == "math"])
    geo = len([f for f in FORMULAS if f["cat"] == "geo"])
    phys = len([f for f in FORMULAS if f["cat"] == "phys"])
    
    score = user_stats[0] if user_stats else 0
    viewed = user_stats[1] if user_stats else 0
    
    await message.answer(
        f"📊 <b>AuraSTEM Statistika</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔵 Matematika: <b>{math} ta</b>\n"
        f"🟢 Geometriya: <b>{geo} ta</b>\n"
        f"🔴 Fizika: <b>{phys} ta</b>\n"
        f"📚 <b>Jami: {len(FORMULAS)} ta formula</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Siz:</b>\n"
        f"⭐ Ball: <b>{score}</b>\n"
        f"👁 Ko‘rilgan: <b>{viewed} ta</b>\n\n"
        f"👨‍💻 @yoldoshev_2",
        parse_mode="HTML"
    )

# ─── /bookmark ────────────────────────
@dp.message(Command("bookmark"))
async def bookmark_command(message: types.Message):
    user = message.from_user
    
    try:
        formula_id = int(message.text.replace("/bookmark", "").strip())
    except:
        await message.answer("📌 Format: /bookmark ID\nMasalan: /bookmark 7", parse_mode="HTML")
        return
    
    f = next((f for f in FORMULAS if f["id"] == formula_id), None)
    if not f:
        await message.answer("❌ Bunday ID li formula topilmadi.", parse_mode="HTML")
        return
    
    async with aiosqlite.connect("aurastem.db") as db:
        await db.execute(
            "INSERT OR REPLACE INTO bookmarks (user_id, formula_id) VALUES (?, ?)",
            (user.id, formula_id)
        )
        await db.commit()
    
    await message.answer(f"⭐ Formula #{formula_id} xatcho‘pga qo‘shildi!", parse_mode="HTML")

# ─── INLINE REJIM ─────────────────────
@dp.inline_query()
async def inline_search(query: InlineQuery):
    text = query.query.strip()
    
    if not text:
        results = FORMULAS[:10]
    else:
        results = [f for f in FORMULAS if 
                   text.lower() in f["title"].lower() or
                   text.lower() in f["label"].lower() or
                   any(text.lower() in tag.lower() for tag in f.get("tags", []))]
    
    items = []
    for f in results[:20]:
        cat_emoji = {"math": "🔵", "geo": "🟢", "phys": "🔴"}
        emoji = cat_emoji.get(f["cat"], "📌")
        
        items.append(InlineQueryResultArticle(
            id=str(f["id"]),
            title=f"{emoji} {f['title']}",
            description=f"🏷 {f['label']} | {' • '.join(f.get('tags', []))}",
            input_message_content=InputTextMessageContent(
                message_text=format_formula_long(f),
                parse_mode="HTML"
            )
        ))
    
    await query.answer(items, cache_time=5)

# ─── OVOZLI XABAR ────────────────────
@dp.message(lambda m: m.voice is not None)
async def voice_search(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Inline qidiruv", switch_inline_query_current_chat="")],
        [InlineKeyboardButton(text="🎲 Tasodifiy formula", callback_data="random")],
    ])
    
    await message.answer(
        "🎙 <b>Ovozli xabar qabul qilindi!</b>\n\n"
        "💡 <b>Tezroq usul:</b>\n"
        "<code>@aura_stembot formula_nomi</code>\n\n"
        "Yoki tugmalardan foydalaning 👇",
        parse_mode="HTML",
        reply_markup=keyboard
    )
    await add_score(message.from_user.id, 5)

# ─── KATEGORIYA TUGMALARI ────────────
@dp.callback_query(lambda c: c.data == "cat_math")
async def cat_math(callback: types.CallbackQuery):
    formulas = [f for f in FORMULAS if f["cat"] == "math"]
    await callback.message.answer(f"🔵 <b>Matematika — {len(formulas)} ta formula</b>", parse_mode="HTML")
    for f in formulas[:5]:
        await callback.message.answer(format_formula(f), parse_mode="HTML")
    await add_score(callback.from_user.id, 5)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "cat_geo")
async def cat_geo(callback: types.CallbackQuery):
    formulas = [f for f in FORMULAS if f["cat"] == "geo"]
    await callback.message.answer(f"🟢 <b>Geometriya — {len(formulas)} ta formula</b>", parse_mode="HTML")
    for f in formulas[:5]:
        await callback.message.answer(format_formula(f), parse_mode="HTML")
    await add_score(callback.from_user.id, 5)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "cat_phys")
async def cat_phys(callback: types.CallbackQuery):
    formulas = [f for f in FORMULAS if f["cat"] == "phys"]
    await callback.message.answer(f"🔴 <b>Fizika — {len(formulas)} ta formula</b>", parse_mode="HTML")
    for f in formulas[:5]:
        await callback.message.answer(format_formula(f), parse_mode="HTML")
    await add_score(callback.from_user.id, 5)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "random")
async def btn_random(callback: types.CallbackQuery):
    f = rnd.choice(FORMULAS)
    await callback.message.answer(format_formula_long(f), parse_mode="HTML")
    await add_score(callback.from_user.id, 3)
    await callback.answer("🎲")

@dp.callback_query(lambda c: c.data == "spin")
async def btn_spin(callback: types.CallbackQuery):
    await spin_command(callback.message)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "quiz_start")
async def btn_quiz(callback: types.CallbackQuery):
    await quiz_command(callback.message)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "challenge_start")
async def btn_challenge(callback: types.CallbackQuery):
    await challenge_command(callback.message)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "leaderboard")
async def btn_leaderboard(callback: types.CallbackQuery):
    await leaderboard_command(callback.message)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "weekly")
async def btn_weekly(callback: types.CallbackQuery):
    await weekly_command(callback.message)
    await callback.answer()

# ─── RENDER WEB SERVER ──────────────
async def handle(request):
    return web.Response(text="AuraSTEM bot is working!\n@yoldoshev_2\n120 formula | Quiz | Spin | Challenge")

async def main():
    await init_db()
    
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 8000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    print(f"🤖 AuraSTEM bot ishga tushdi! {len(FORMULAS)} ta formula yuklandi.")
    print(f"👨‍💻 Muallif: @yoldoshev_2")
    print(f"🎮 Funksiyalar: Quiz | Spin | Challenge | Inline | Voice | Leaderboard")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
