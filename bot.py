import os
import json
import csv

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")

ADMIN_IDS = [7352664827]

if not BOT_TOKEN or not WEBAPP_URL:
    raise ValueError("BOT_TOKEN yoki WEBAPP_URL kiritilmagan!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

orders = {}


# ASOSIY MENYU
@dp.message(CommandStart())
async def start(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="🛋 Buyurtma berish",
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            ],
            [KeyboardButton(text="📞 Bog‘lanish")]
        ],
        resize_keyboard=True
    )

    await message.answer(
        "🏠 KAO MEBEL rasmiy botiga xush kelibsiz!\n\n"
        "Bu yerda mebel buyurtma qilishingiz mumkin.",
        reply_markup=keyboard
    )


# BOG‘LANISH
@dp.message(F.text == "📞 Bog‘lanish")
async def contact(message: Message):
    await message.answer(
        "📞 KAO MEBEL\n"
        "Buyurtma berish uchun «🛋 Buyurtma berish» tugmasini bosing."
    )


# MINI APP'DAN KELGAN BUYURTMA
@dp.message(F.web_app_data)
async def get_order(message: Message):
    try:
        data = json.loads(message.web_app_data.data)

        if data.get("type") != "order":
            await message.answer("❌ Buyurtma ma’lumotlari noto‘g‘ri.")
            return

        name = str(data.get("name", ""))[:100]
        phone = str(data.get("phone", ""))[:30]
        items = data.get("items", [])

        if not name or not phone or not isinstance(items, list):
            await message.answer("❌ Ma’lumotlarni qayta tekshiring.")
            return

        order_id = message.from_user.id

        orders[order_id] = {
            "name": name,
            "phone": phone,
            "items": items
        }

        keyboard = ReplyKeyboardMarkup(
            keyboard=[[
                KeyboardButton(
                    text="📍 Joylashuvni yuborish",
                    request_location=True
                )
            ]],
            resize_keyboard=True,
            one_time_keyboard=True
        )

        await message.answer(
            "✅ Buyurtmangiz qabul qilindi!\n\n"
            "📍 Endi yetkazib berish manzilingizni yuboring.",
            reply_markup=keyboard
        )

    except Exception:
        await message.answer(
            "❌ Xatolik yuz berdi. Iltimos, qayta urinib ko‘ring."
        )


# MIJOZ JOYLASHUVINI YUBORADI
@dp.message(F.location)
async def get_location(message: Message):
    user_id = message.from_user.id

    if user_id not in orders:
        await message.answer("Avval buyurtma berishingiz kerak.")
        return

    order = orders.pop(user_id)

    order_text = (
        "🛍 YANGI BUYURTMA — KAO MEBEL\n\n"
        f"👤 Ism: {order['name']}\n"
        f"📞 Telefon: {order['phone']}\n"
        f"🛋 Mahsulotlar: {json.dumps(order['items'], ensure_ascii=False)}\n"
        f"🆔 Telegram ID: {user_id}\n\n"
        "📍 Mijoz joylashuvi quyida:"
    )

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, order_text)
            await bot.send_location(
                admin_id,
                latitude=message.location.latitude,
                longitude=message.location.longitude
            )
        except Exception as error:
            print("Admin xabari yuborilmadi:", error)

    await message.answer(
        "🎉 Rahmat! Buyurtmangiz yuborildi.\n"
        "Tez orada siz bilan bog‘lanamiz."
    )


# BOTNI ISHGA TUSHIRISH
async def main():
    print("KAO MEBEL bot ishga tushdi!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
