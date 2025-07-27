import os
import httpx
import logging
from fastapi import FastAPI, Request

app = FastAPI()
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ["BOT_TOKEN"]
OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

@app.post("/")
async def root(request: Request):
    data = await request.json()
    logging.info(f"User message: {data}")

    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"]["text"]

        ai_reply = await ask_openrouter(user_message)

        await send_message(chat_id, ai_reply or "مشکلی در پاسخ‌دهی به وجود آمده.")

    return {"ok": True}

async def ask_openrouter(user_message: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistralai/mistral-7b-instruct:free",  # ✅ مدل رایگان
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_message}
        ]
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        logging.error(f"Error contacting AI: {e}")
        return None

async def send_message(chat_id: int, text: str):
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    async with httpx.AsyncClient() as client:
        await client.post(TELEGRAM_API_URL + "sendMessage", json=payload)
