import logging
import httpx
from fastapi import FastAPI, Request
import uvicorn

app = FastAPI()
logging.basicConfig(level=logging.INFO)

# 🔐 توکن ربات تلگرام شما
TELEGRAM_BOT_TOKEN = "7592422208:AAEgrZ09KpWltyJDMyqGutb6dgovii8T-xM"

# 🔐 کلید API گرفته‌شده از OpenRouter
OPENROUTER_API_KEY = "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"

# 🧠 تابع پرسش از OpenRouter
async def ask_openrouter(message: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistralai/mistral-7b-instruct:free",
        "messages": [
            {"role": "user", "content": message}
        ]
    }
    try:
        response = httpx.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logging.error(f"❌ Error contacting AI: {e}")
        return "متاسفم، مشکلی در اتصال به هوش مصنوعی پیش آمده."

# 📤 ارسال پاسخ به کاربر تلگرام
async def send_message(chat_id: int, text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)

# 📥 دریافت پیام از وب‌هوک تلگرام
@app.post("/")
async def webhook(request: Request):
    data = await request.json()
    logging.info(f"📩 User message: {data}")
    message = data.get("message", {})
    text = message.get("text")
    chat_id = message.get("chat", {}).get("id")

    if text and chat_id:
        reply = await ask_openrouter(text)
        await send_message(chat_id, reply)

    return {"ok": True}

# 🚀 اجرای لوکال (در زمان تست)
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
