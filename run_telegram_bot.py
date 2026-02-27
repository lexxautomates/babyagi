#!/usr/bin/env python3
"""
Quick launcher for BabyAGI Telegram Bot
"""

import os
import sys

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Check for required environment variables
token = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')
openai_key = os.getenv('OPENAI_API_KEY')

print("=" * 50)
print("BabyAGI Telegram Bot Launcher")
print("=" * 50)
print(f"Telegram Bot Token: {'✓ Set' if token else '✗ Missing'}")
print(f"Telegram Chat ID: {'✓ Set' if chat_id else '✗ Missing'}")
print(f"OpenAI API Key: {'✓ Set' if openai_key and openai_key != 'your_openai_api_key_here' else '✗ Not configured (optional for basic chat)'}")
print("=" * 50)

if not token:
    print("\n❌ Error: TELEGRAM_BOT_TOKEN is required!")
    print("Please set it in the .env file")
    sys.exit(1)

if not chat_id:
    print("\n⚠️ Warning: TELEGRAM_CHAT_ID is not set!")
    print("Anyone will be able to use your bot.")

print("\n🚀 Starting Telegram Bot...")
print("Send /start to your bot on Telegram to begin!\n")

# Import and run the bot
from telegram_bot import main
main()