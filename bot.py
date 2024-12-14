import logging
import asyncio
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message
import os

# Environment variable for token
API_TOKEN = os.getenv('TELEGRAM_TOKEN')

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# /start command handler
@router.message(commands=["start"])
async def start_command(message: Message):
    await message.reply("Hello! I'm your Aiogram bot. How can I assist you today?")

# /help command handler
@router.message(commands=["help"])
async def help_command(message: Message):
    await message.reply("Use /start to start interacting with me or /help for assistance.")

# Default message handler
@router.message()
async def echo_message(message: Message):
    await message.answer(f"You said: {message.text}")

# Main function to start the bot
async def main():
    try:
        logging.info("Starting bot...")
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
