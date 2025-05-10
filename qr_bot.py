import logging
import os
import io
import qrcode
import asyncio
from flask import Flask
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get the token from environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Missing BOT_TOKEN environment variable")

# Telegram command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 Hello! I'm a QR Bot developed by Yaqoob Khan. /Send me any text and I will generate a QR code for it!"
    )

# Generate QR from any text
async def generate_qr(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    qr = qrcode.make(text)
    img_byte_arr = io.BytesIO()
    qr.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    await update.message.reply_photo(photo=img_byte_arr, caption=f"QR Code for: {text}")

# Run the bot
async def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_qr))

    logger.info("Bot started via polling...")
    await application.run_polling()  # ✅ Correct usage

if __name__ == '__main__':
    asyncio.run(main())
