import logging
import os
import asyncio
import signal
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
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
    welcome_message = (
        "👋 Welcome to the QR Code Generator Bot!\n\n"
        "Simply send me any text, and I'll generate a QR code for it.\n"
        "The QR code will be sent back as a PNG image."
    )
    await update.message.reply_text(welcome_message)

async def generate_qr(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate a QR code from the user's message and send it back."""
    try:
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
    except Exception as e:
        logger.error(f"Error generating QR code: {e}")
        await update.message.reply_text("Sorry, there was an error generating your QR code. Please try again.")

async def health_check(request):
    """Health check endpoint for Render."""
    return web.Response(text="Bot is running!")

async def shutdown(signal, loop):
    """Cleanup tasks tied to the service's shutdown."""
    logger.info(f"Received exit signal {signal.name}...")
    
    if application:
        logger.info("Stopping application...")
        await application.stop()
        await application.shutdown()
    
    if runner:
        logger.info("Cleaning up web server...")
        await runner.cleanup()
    
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    if tasks:
        logger.info(f"Cancelling {len(tasks)} outstanding tasks")
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
    
    logger.info("Shutdown complete")
    loop.stop()

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the bot."""
    logger.error(f"Exception while handling an update: {context.error}")

def main() -> None:
    """Start the bot."""
    try:
        global application, runner
        
        # Create the Application
        application = Application.builder().token(TOKEN).build()

        # Add error handler
        application.add_error_handler(error_handler)

        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_qr))

        # Start the bot
        logger.info("Starting bot...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        logger.info("Bot started successfully")

    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot stopped due to error: {e}") 
