import logging
import httpx
from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List, Dict
import os

TELEGRAM_BOT_TOKEN = "7592422208:AAEgrZ09KpWltyJDMyqGutb6dgovii8T-xM"
OPENROUTER_API_KEY = "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"

app = FastAPI()
logging.basicConfig(level=logging.INFO)

class TelegramMessage(BaseModel):
    message: Dict

async def get_free_model():
    url = "https://openrouter.ai/api/v1/models"
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        models = response.json().get("data", [])
        for model in models:
            if model.get("pricing", {}).get("prompt") == 0:
                return model["id"]
    return None  # اگر هیچ مدل رایگانی نبود

async def ask_ai(message: str, model: str):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message}
        ]
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

async def send_message(chat_id: int, text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    async with httpx.AsyncClient() as client:
        await client.post(url, data=data)

@app.post("/")
async def webhook(req: TelegramMessage):
    message = req.message.get("text", "")
    chat_id = req.message["chat"]["id"]

    logging.info(f"User message: {message}")

    try:
        model = await get_free_model()
        if not model:
            await send_message(chat_id, "مدل رایگانی پیدا نشد. لطفاً بعداً تلاش کن.")
            return {"status": "no free model"}

        reply = await ask_ai(message, model)
        await send_message(chat_id, reply)
    except Exception as e:
        logging.error(f"Error contacting AI: {e}")
        await send_message(chat_id, "خطا در اتصال به مدل هوش مصنوعی.")

    return {"status": "ok"}
