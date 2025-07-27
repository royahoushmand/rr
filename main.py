import os
import logging
import httpx
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# بارگذاری متغیرهای محیطی
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# تنظیمات لاگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    logger.info(f"User message: {user_message}")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://github.com/royahoushmand/rr",
        "X-Title": "RoyaBot"
    }

    data = {
        "model": "openai/gpt-3.5-turbo",  # یا مثلاً "google/gemini-pro"
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_message}
        ]
    }

    try:
        response = httpx.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        ai_reply = response.json()["choices"][0]["message"]["content"]
        logger.info(f"AI reply: {ai_reply}")
    except Exception as e:
        logger.error(f"Error contacting AI: {e}")
        ai_reply = "❌ مشکلی در ارتباط با هوش مصنوعی پیش آمد."

    await update.message.reply_text(ai_reply)

def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is required.")
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY is required.")

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    application.add_handler(message_handler)

    # اگر روی Render اجرا می‌کنی و webhook ست شده
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_url=os.environ.get("WEBHOOK_URL")  # باید در env ست شده باشه
    )

if __name__ == '__main__':
    main()
