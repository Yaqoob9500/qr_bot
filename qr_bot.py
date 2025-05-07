import logging
import os
import qrcode
import io
import asyncio
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot Token and Webhook Settings
BOT_TOKEN = os.environ.get("BOT_TOKEN", "7752871738:AAEap1HC4Ns19vgPp3EQhqiJfBh-ocFiIXE")
APP_URL = os.environ.get("APP_URL", "https://qr_bot.onrender.com")  # Your Render URL

# Flask App
app = Flask(__name__)

# Telegram Bot Application
application = Application.builder().token(BOT_TOKEN).build()

# Telegram Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to the QR Code Generator Bot!\n\n"
        "Send any text and I'll reply with a QR code image."
    )

async def generate_qr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(text)
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="black", back_color="white")

    img_bytes = io.BytesIO()
    qr_image.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    await update.message.reply_photo(photo=img_bytes, caption=f"Here's your QR code for: {text}")

# Register Handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_qr))

# Flask Webhook Route
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "OK"

# Set webhook using asyncio before server starts
async def setup_webhook():
    bot = Bot(token=BOT_TOKEN)
    await bot.set_webhook(f"{APP_URL}/{BOT_TOKEN}")
    logger.info("Webhook set to: %s/%s", APP_URL, BOT_TOKEN)

# Start everything
if __name__ == "__main__":
    # Setup webhook before running Flask
    asyncio.run(setup_webhook())
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
