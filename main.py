import logging
import os
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram import Update

# تنظیم لاگ‌ها
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Received /start command from user {update.effective_user.id}")
    await update.message.reply_text("سلام! من آنلاینم و از طریق webhook کار می‌کنم 🙂")

# پیام‌های متنی
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Received text message from user {update.effective_user.id}: {update.message.text}")
    await update.message.reply_text(f"شما گفتید: {update.message.text}")

# main
def main():
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN environment variable not set.")
        raise ValueError("BOT_TOKEN is required.")
    
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    PORT = int(os.environ.get("PORT", "8000"))
    WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
    if not WEBHOOK_URL:
        logger.error("WEBHOOK_URL environment variable not set.")
        raise ValueError("WEBHOOK_URL is required.")
    
    WEBHOOK_PATH = BOT_TOKEN
    logger.info(f"Starting webhook on port {PORT} with URL: {WEBHOOK_URL}/{WEBHOOK_PATH}")
    
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=WEBHOOK_PATH,
        webhook_url=f"{WEBHOOK_URL}/{WEBHOOK_PATH}"
    )

if __name__ == "__main__":
    main()
