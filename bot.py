import os
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from groq import Groq
import asyncio

from faq import SYSTEM_PROMPT

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
GROQ_API_KEY = os.environ["GROQ_API_KEY"]

client = Groq(api_key=GROQ_API_KEY)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

WELCOME_MESSAGE = (
    "Сәлеметсіз бе! 👋\n\n"
    "Мен — Костоправ Ерланның чат-ассистентімін.\n"
    "Мануальды терапия, омыртқа, буын және бел ауруы туралы "
    "сұрақтарыңызға жауап бере аламын.\n\n"
    "Сұрағыңызды жазыңыз немесе /help командасын қолданыңыз."
)

HELP_MESSAGE = (
    "📋 *Қызметтер тізімі:*\n\n"
    "🧘 Омыртқаны емдеу (остеохондроз, грыжа, сколиоз)\n"
    "🦵 Буын ауруы (артроз, артрит)\n"
    "⚡ Жүйке қысылуы (радикулит, ишиас)\n"
    "💪 Бұлшықет спазмы мен жарақат\n"
    "🧠 Бас ауруы, мигрень\n"
    "🏃 Спорттық жарақат\n\n"
    "📞 *Жазылу:* 8 705 555 61 64 (WhatsApp/телефон)\n"
    "🕐 *Жұмыс уақыты:* Дс–Сб, 09:00–19:00\n\n"
    "Сұрағыңызды жазыңыз — жауап берейін!"
)


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(WELCOME_MESSAGE)


@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer(HELP_MESSAGE, parse_mode="Markdown")


@dp.message(F.text)
async def handle_message(message: Message):
    logger.info("Сұрақ: %s", message.text)

    await bot.send_chat_action(chat_id=message.chat.id, action="typing")

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message.text},
            ],
            max_tokens=1024,
        )
        reply = response.choices[0].message.content
    except Exception as e:
        logger.error("Groq қатесі: %s", e)
        reply = (
            "Кешіріңіз, қазір жауап бере алмадым. 😔\n"
            "Тікелей байланысыңыз: 8 705 555 61 64 (WhatsApp)"
        )

    await message.answer(reply)


async def main():
    logger.info("Бот іске қосылды...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
