import logging
import httpx
import os
from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Dict
import traceback

# راه‌اندازی لاگر
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# توکن‌ها از محیط خوانده می‌شوند
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# بررسی اولیه برای وجود توکن‌ها
if not TELEGRAM_BOT_TOKEN:
    logging.error("❌ TELEGRAM_BOT_TOKEN تنظیم نشده است.")
if not OPENAI_API_KEY:
    logging.error("❌ OPENAI_API_KEY تنظیم نشده است.")

app = FastAPI()

class TelegramMessage(BaseModel):
    message: Dict

async def send_message(chat_id: int, text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data)
            response.raise_for_status()
    except Exception as e:
        logging.error("❌ خطا در ارسال پیام تلگرام:")
        logging.error(traceback.format_exc())

async def ask_gpt(message: str) -> str:
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message}
        ]
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        logging.error("❌ خطا در دریافت پاسخ از GPT:")
        logging.error(traceback.format_exc())
        raise

@app.post("/")
async def webhook(req: TelegramMessage):
    try:
        message = req.message.get("text", "")
        chat_id = req.message["chat"]["id"]

        logging.info(f"📩 پیام کاربر: {message}")

        reply = await ask_gpt(message)
        await send_message(chat_id, reply)

    except Exception as e:
        logging.error("❌ خطای کلی در webhook:")
        logging.error(traceback.format_exc())
        if "chat_id" in locals():
            await send_message(chat_id, "❌ خطایی در سرور رخ داده است.")

    return {"status": "ok"}
