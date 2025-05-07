import logging
import os
import qrcode
import io
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot Token and Webhook Settings
BOT_TOKEN = os.environ.get("BOT_TOKEN", "7752871738:AAEap1HC4Ns19vgPp3EQhqiJfBh-ocFiIXE")  # Set in Render environment variables
RENDER_URL = os.environ.get("RENDER_URL", "https://qr_bot.onrender.com")  # Your Render URL

# Flask App
app = Flask(__name__)
application = Application.builder().token(BOT_TOKEN).build()

# Telegram Bot Handlers
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

# Flask Route for Webhook
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "OK"

# Set Webhook on startup
@app.before_first_request
def set_webhook():
    from telegram import Bot
    bot = Bot(token=BOT_TOKEN)
    bot.set_webhook(f"{RENDER_URL}/{BOT_TOKEN}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
