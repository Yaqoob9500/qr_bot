import logging
import os
import asyncio
import signal
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, Update  # Correct import
import qrcode
from PIL import Image
import io
from aiohttp import web

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get configuration from environment variables
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    raise ValueError("No TELEGRAM_BOT_TOKEN found in environment variables")

PORT = int(os.getenv('PORT', 8080))

# Global variables for cleanup
application = None
runner = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the command /start is issued."""
    logger.info(f"Received /start command from user {update.effective_user.id}")
    welcome_message = (
        "👋 Welcome to the QR Code Generator Bot!\n\n"
        "Simply send me any text, and I'll generate a QR code for it.\n"
        "The QR code will be sent back as a PNG image."
    )
    await update.message.reply_text(welcome_message)
    logger.info(f"Sent welcome message to user {update.effective_user.id}")

async def generate_qr(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate a QR code from the user's message and send it back."""
    try:
        text = update.message.text
        logger.info(f"Received message from user {update.effective_user.id}: {text}")

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)
        qr_image = qr.make_image(fill_color="black", back_color="white")

        img_byte_arr = io.BytesIO()
        qr_image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        await update.message.reply_photo(
            photo=img_byte_arr,
            caption=f"Here's your QR code for: {text}"
        )
        logger.info(f"Sent QR code to user {update.effective_user.id}")
    except Exception as e:
        logger.error(f"Error generating QR code: {e}")
        await update.message.reply_text("Sorry, there was an error generating your QR code. Please try again.")

async def health_check(request):
    """Health check endpoint for Render."""
    return web.Response(text="Bot is running!")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the bot."""
    logger.error(f"Exception while handling an update: {context.error}")

async def main() -> None:
    """Start the bot and web server."""
    global application, runner

    application = (
        Application.builder()
        .token(TOKEN)
        .concurrent_updates(True)
        .build()
    )

    application.add_error_handler(error_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_qr))

    app = web.Application()
    app.router.add_get('/', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    logger.info(f"Web server started on port {PORT}")

    try:
        await application.bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        logger.warning(f"Webhook removal failed: {e}")

    logger.info("Bot is starting polling...")
    await application.run_polling(
        close_loop=False,
        drop_pending_updates=True,
    )

if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(main())
        else:
            loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot stopped due to error: {e}")
