from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, filters
import requests
import datetime
from notion_client import Client

# Telegram Bot Token
TELEGRAM_TOKEN = "7808291028:AAGRsVUGT2id7yrO_XaRPlYBtoYLYb_jzcg"
bot = Bot(token=TELEGRAM_TOKEN)

# PaxSenix API URLs
TEXT_API_URL = "https://api.paxsenix.biz.id/ai/gpt4o"
IMAGE_API_URL = "https://api.paxsenix.biz.id/ai/geminivision"

# Notion Integration
NOTION_TOKEN = "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"
NOTION_DATABASE_ID = "15b7280d4cf580d7a8e1dd7b0bf981fa"
notion = Client(auth=NOTION_TOKEN)

# Save messages to Notion
def save_to_notion(user_text, bot_response):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    notion.pages.create(
        parent={"database_id": NOTION_DATABASE_ID},
        properties={
            "Timestamp": {"title": [{"text": {"content": timestamp}}]},
            "User Message": {"rich_text": [{"text": {"content": user_text}}]},
            "Bot Response": {"rich_text": [{"text": {"content": bot_response}}]},
        }
    )

# Handle text messages
async def handle_text(update: Update, context: CallbackContext):
    user_text = update.message.text
    chat_id = update.message.chat_id

    # Call PaxSenix GPT-4o API
    response = requests.post(TEXT_API_URL, headers={
        "accept": "application/json",
        "Content-Type": "application/json"
    }, json={"messages": [{"role": "user", "content": user_text}]})

    response_text = response.json().get("message", "I couldn't process your request.")
    await context.bot.send_message(chat_id=chat_id, text=response_text)

    # Save to Notion
    save_to_notion(user_text, response_text)

# Handle photo messages
async def handle_photo(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    user_caption = update.message.caption or "Please Describe this Image"

    # Get photo file ID
    photo_file_id = update.message.photo[-1].file_id  # Highest resolution
    file = await context.bot.get_file(photo_file_id)
    file_url = file.file_path

    # Call PaxSenix GeminiVision API
    image_response = requests.get(f"{IMAGE_API_URL}?text={user_caption}&url={file_url}", headers={
        "accept": "application/json"
    })

    response_text = image_response.json().get("message", "I couldn't process the image.")
    await context.bot.send_message(chat_id=chat_id, text=response_text)

    # Save to Notion
    save_to_notion(f"Image Caption: {user_caption}", response_text)

# Start the bot
def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Handlers
    text_handler = MessageHandler(filters.TEXT, handle_text)
    photo_handler = MessageHandler(filters.PHOTO, handle_photo)

    # Add handlers
    application.add_handler(text_handler)
    application.add_handler(photo_handler)

    # Start polling
    application.run_polling()

if __name__ == "__main__":
    main()
