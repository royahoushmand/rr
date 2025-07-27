import logging
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update

# تنظیم لاگ‌ها برای مشاهده خطا یا وضعیت اجرا
logging.basicConfig(level=logging.INFO)

# تعریف دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! من آنلاینم و از طریق polling کار می‌کنم 🙂")

# اجرای برنامه با polling
if __name__ == "__main__":
    application = ApplicationBuilder().token("7592422208:AAEgrZ09KpWltyJDMyqGutb6dgovii8T-xM").build()

    # اضافه کردن دستور /start
    application.add_handler(CommandHandler("start", start))

    # اجرای polling (بدون webhook)
    application.run_polling()
