import logging
import os
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram import Update

# تنظیم لاگ‌ها برای مشاهده خطا یا وضعیت اجرا
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(name)

# تعریف دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Received /start command from user {update.effective_user.id}")
    await update.message.reply_text("سلام! من آنلاینم و از طریق webhook کار می‌کنم 🙂")

# تعریف تابع برای پاسخ به پیام‌های متنی عادی
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Received text message from user {update.effective_user.id}: {update.message.text}")
    # ربات همان متنی را که کاربر فرستاده، به او برمی‌گرداند.
    await update.message.reply_text(f"شما گفتید: {update.message.text}")

# تابع اصلی برای اجرای ربات
def main():
    # توکن ربات را از متغیر محیطی BOT_TOKEN دریافت می‌کنیم
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN environment variable not set.")
        raise ValueError("BOT_TOKEN environment variable is required.")

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # اضافه کردن CommandHandler برای دستور /start
    application.add_handler(CommandHandler("start", start))

    # اضافه کردن MessageHandler برای پیام‌های متنی
    # filters.TEXT اطمینان می‌دهد که فقط پیام‌های متنی پردازش شوند.
    # ~filters.COMMAND اطمینان می‌دهد که دستورات (مثل /start) دوباره توسط این هندلر پردازش نشوند.
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # --- تنظیمات Webhook برای Render ---
    PORT = int(os.environ.get("PORT", "8000"))
    WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
    if not WEBHOOK_URL:
        logger.error("WEBHOOK_URL environment variable not set.")
        raise ValueError("WEBHOOK_URL environment variable is required.")

    WEBHOOK_PATH = BOT_TOKEN # یا یک مسیر دلخواه دیگر

    logger.info(f"Starting webhook on port {PORT} with URL: {WEBHOOK_URL}/{WEBHOOK_PATH}")

    # اجرای برنامه با webhook
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=WEBHOOK_PATH,
        webhook_url=f"{WEBHOOK_URL}/{WEBHOOK_PATH}"
    )

if name == "main":
    main()