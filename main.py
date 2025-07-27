import logging
import httpx
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# 🔐 توکن‌ها (برای تست مستقیم در کد)
TELEGRAM_BOT_TOKEN = "7592422208:AAEgrZ09KpWltyJDMyqGutb6dgovii8T-xM"
OPENROUTER_API_KEY = "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"

# 📦 مدل هوش مصنوعی رایگان (DeepSeek V3)
MODEL = "deepseek-ai/deepseek-coder:free"

# 📋 تنظیمات لاگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 📨 ارسال پیام به OpenRouter
async def ask_ai(message: str) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    json_data = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": message}
        ]
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=json_data)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Error contacting AI: {e}")
        return "خطا در اتصال به هوش مصنوعی. لطفاً بعداً دوباره تلاش کنید."

# 🤖 پاسخ به پیام کاربر
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    logger.info(f"User message: {user_message}")
    ai_response = await ask_ai(user_message)
    await update.message.reply_text(ai_response)

# 🚀 اجرای ربات
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Bot started...")
    app.run_polling()
