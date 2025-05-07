import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import qrcode
from PIL import Image
import io
import requests

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
TOKEN = '7752871738:AAEap1HC4Ns19vgPp3EQhqiJfBh-ocFiIXE'
WEBHOOK_URL = 'https://qr_bot.onrender.com/webhook'  # Replace with your hosted URL

# Initialize the Flask app
app = Flask(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the command /start is issued."""
    welcome_message = (
        "👋 Welcome to the QR Code Generator Bot!\n\n"
        "Simply send me any text, and I'll generate a QR code for it.\n"
        "The QR code will be sent back as a PNG image."
    )
    await update.message.reply_text(welcome_message)

async def generate_qr(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate a QR code from the user's message and send it back."""
    # Get the text from the user's message
    text = update.message.text
    
    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    # Add data to QR code
    qr.add_data(text)
    qr.make(fit=True)
    
    # Create an image from the QR code
    qr_image = qr.make_image(fill_color="black", back_color="white")
    
    # Convert the image to bytes
    img_byte_arr = io.BytesIO()
    qr_image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    # Send the QR code image
    await update.message.reply_photo(
        photo=img_byte_arr,
        caption=f"Here's your QR code for: {text}"
    )

# Error handler
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors and notify the user."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    if update and hasattr(update, 'message'):
        await update.message.reply_text("⚠️ An unexpected error occurred. Please try again later.")

# Create the Application
application = Application.builder().token(TOKEN).build()

# Add handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_qr))

# Register the error handler
application.add_error_handler(error_handler)

# Set up webhook route in Flask
@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhook updates from Telegram."""
    json_str = request.get_data(as_text=True)
    logger.info(f"Received update: {json_str}")  # Log incoming request
    update = Update.de_json(json_str, application.bot)
    application.process_update(update)
    return 'OK'

def set_webhook():
    """Set the webhook for your bot."""
    url = 'https://api.telegram.org/bot' + TOKEN + '/setWebhook?url=' + WEBHOOK_URL
    response = requests.get(url)
    print(response.json())  # To verify the result of setting the webhook

if __name__ == '__main__':
    # Set the webhook for the bot
    set_webhook()

    # Run the Flask web server to handle webhook requests
    app.run(host='0.0.0.0', port=5000)
