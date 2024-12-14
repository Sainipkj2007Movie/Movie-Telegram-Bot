import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import os

API_TOKEN = os.getenv('TELEGRAM_TOKEN')  # Set the bot token as an environment variable

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Start command handler
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.reply("Hello! I'm your Aiogram bot. How can I help you today?")

# Help command handler
@dp.message_handler(commands=['help'])
async def cmd_help(message: types.Message):
    await message.reply("You can interact with me using /start or /help.")

# Default message handler
@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(f"Echo: {message.text}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
