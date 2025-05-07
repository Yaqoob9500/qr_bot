# Telegram QR Code Generator Bot

A simple Telegram bot that generates QR codes from text messages.

## Features

- Generates QR codes from any text message
- Sends QR codes as PNG images
- Simple and easy to use interface

## Setup

1. Create a new bot and get your token from [@BotFather](https://t.me/BotFather) on Telegram

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Edit `qr_bot.py` and replace `'YOUR_BOT_TOKEN'` with your actual bot token

4. Run the bot:
   ```bash
   python qr_bot.py
   ```

## Usage

1. Start a chat with your bot on Telegram
2. Send `/start` to get the welcome message
3. Send any text message to generate a QR code
4. The bot will reply with a PNG image containing the QR code

## Requirements

- Python 3.7 or higher
- python-telegram-bot (v20+)
- qrcode
- Pillow 