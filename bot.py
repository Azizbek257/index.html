import asyncio
import json
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = "8927865338:AAFEaaHuZqlDTYc6lne-MMFcR8Vrl4KsIB0"
ADMIN_ID = 8767254359
WEB_APP_URL = "https://azizbek257.github.io/Test_titul/"
DB_FILE = "test_keys.json"

if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f:
        TEST_KEYS = json.load(f)
else:
    TEST_KEYS = {"1024": "ABCDEABCDEABCDEABCDEABCDEABCDE"}
    with open(DB_FILE, "w") as f:
        json.dump(TEST_KEYS, f)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def save_keys():
    with open(DB_FILE, "w") as f:
        json.dump(TEST_KEYS, f, indent=4)

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Davlatcha varaqani ochish 📝", web_app=WebAppInfo(url=WEB_APP_URL))]]
    )
    welcome_text = (
        f"Salom, {message.from_user.full_name}!\n"
        "<b>Doimobod EDU</b> professional DTM javoblar varaqasi botiga xush kelibsiz.\n\n"
        "Javoblaringizni belgilash va topshirish uchun pastdagi tugmani bosing."
    )
    if message.from_user.id == ADMIN_ID:
        welcome_text += (
            "\n\n⚙️ <b>ADMIN PANEL YO'RIQNOMASI:</b>\n"
            "Yangi test qo'shish: <code>+kod*KALITLAR</code>\n"
            "Mavjud testni o'chirish: <code>-kod</code>\n"
            "Barcha testlar ro'yxati: /list"
        )
    await message.answer(welcome_text, reply_markup=markup, parse_mode="HTML")

@dp.message(Command("list"))
async def list_tests(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    if not TEST_KEYS:
        await message.answer("Bazada hech qanday test kaliti mutable emas.")
        return
    text = "🔑 <b>Bazadagi mavjud testlar:</b>\n\n"
    for code, key in TEST_KEYS.items():
        text += f"📌 <b>Kod:</b> <code>{code}</code>\n🔑 <b>Kalit:</b> <code>{key}</code>\n\n"
    await message.answer(text, parse_mode="HTML")

@dp.message(F.text.startswith("+") & (F.from_user.id == ADMIN_ID))
async def add_test_key(message: types.Message):
    try:
        raw_text = message.text[1:]
        if "*" not in raw_text:
            await message.answer("❌ Xato format! Namuna: +1025*ABBCCDD...")
            return
        test_code, keys = raw_text.split("*", 1)
        test_code = test_code.strip()
        keys = keys.strip().upper()
        if len(keys) != 30:
            await message.answer(f"⚠️ Kalitlar soni 30 ta bo'lishi kerak. Siz {len(keys)} ta kiritdingiz.")
            return
        TEST_KEYS[test_code] = keys
        save_keys()
        await message.answer(f"✅ Yangi test saqlandi!\n📌 <b>Kod:</b> {test_code}\n🔑 <b>Kalitlar:</b> {keys}", parse_mode="HTML")
    except Exception as e:
        await message.answer(f"Xatolik: {str(e)}")

@dp.message(F.text.startswith("-") & (F.from_user.id == ADMIN_ID))
async def delete_test_key(message: types.Message):
    test_code = message.text[1:].strip()
    if test_code in TEST_KEYS:
        del TEST_KEYS[test_code]
        save_keys()
        await message.answer(f"🗑 <b>{test_code}</b> kodli test o'chirildi.")
    else:
        await message.answer(f"❌ Test topilmadi.")

@dp.message(lambda message: message.web_app_data is not None)
async def handle_web_app_data(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
        student_name = data.get("student_name")
        test_code = str(data.get("test_code"))
        student_answers = data.get("answers").upper()
        
        if test_code not in TEST_KEYS:
            await message.answer(f"❌ Tizimda <b>{test_code}</b> kodli test topilmadi!", parse_mode="HTML")
            return
            
        correct_answers = TEST_KEYS[test_code]
        correct_count, wrong_count, details = 0, 0, ""
        
        for i in range(len(correct_answers)):
            st_ans = student_answers[i] if i < len(student_answers) else "Yo'q"
            cor_ans = correct_answers[i]
            if st_ans == cor_ans:
                correct_count += 1
                details += f"<b>{i+1}</b>) ✅ (Siz: {st_ans})\n"
            else:
                wrong_count += 1
                details += f"<b>{i+1}</b>) ❌ (Siz: {st_ans} | To'g'ri: {cor_ans})\n"
                
        percent = (correct_count / len(correct_answers)) * 100
        result_msg = (
            f"📊 <b>TEST NATIJASI (Doimobod EDU)</b>\n\n"
            f"👤 <b>Abituriyent:</b> {student_name}\n"
            f"🔑 <b>Test kodi:</b> {test_code}\n"
            f"✅ <b>To'g'ri:</b> {correct_count} ta\n"
            f"❌ <b>Xato:</b> {wrong_count} ta\n"
            f"📈 <b>Natija:</b> {percent:.1f}%\n\n"
            f"📝 <b>Tahlil:</b>\n{details}"
        )
        await message.answer(result_msg, parse_mode="HTML")
        
        admin_report = (
            f"🔔 <b>YANGI NATIJA KELDI!</b>\n\n"
            f"👤 <b>O'quvchi:</b> {student_name}\n"
            f"🔑 <b>Test kodi:</b> {test_code}\n"
            f"✅ <b>To'g'ri:</b> {correct_count} ta\n"
            f"📈 <b>Ko'rsatkich:</b> {percent:.1f}%"
        )
        await bot.send_message(chat_id=ADMIN_ID, text=admin_report, parse_mode="HTML")
    except Exception as e:
        await message.answer(f"Xatolik: {str(e)}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
