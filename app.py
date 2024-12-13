from flask import Flask, request
import threading
from notion_client import Client
import datetime
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters

app = Flask(__name__)

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

def send_typing_action(chat_id):
    """
    Sends typing action to Telegram to show typing status.
    """
    bot.send_chat_action(chat_id=chat_id, action="typing")

def save_to_notion(user_text, bot_response):
    """
    Saves the user and bot messages to a Notion database.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    notion.pages.create(
        parent={"database_id": NOTION_DATABASE_ID},
        properties={
            "Timestamp": {"title": [{"text": {"content": timestamp}}]},
            "User Message": {"rich_text": [{"text": {"content": user_text}}]},
            "Bot Response": {"rich_text": [{"text": {"content": bot_response}}]},
        }
    )

def handle_text_message(update: Update, context):
    chat_id = update.message.chat_id
    user_text = update.message.text

    # Start typing status
    threading.Thread(target=send_typing_action, args=(chat_id,)).start()

    # Call PaxSenix GPT-4o API
    response = requests.post(TEXT_API_URL, headers={
        "accept": "application/json",
        "Content-Type": "application/json"
    }, json={"messages": [{"role": "user", "content": user_text}]})

    response_text = response.json().get("message", "I couldn't process your request.")
    bot.send_message(chat_id=chat_id, text=response_text)

    # Save to Notion
    save_to_notion(user_text, response_text)

def handle_photo_message(update: Update, context):
    chat_id = update.message.chat_id
    user_caption = update.message.caption or "Please Describe this Image"

    # Get the file ID of the photo
    photo_file_id = update.message.photo[-1].file_id  # Highest resolution
    file = bot.get_file(photo_file_id)
    file_url = file.file_url

    # Call PaxSenix GeminiVision API
    image_response = requests.get(f"{IMAGE_API_URL}?text={user_caption}&url={file_url}", headers={
        "accept": "application/json"
    })

    response_text = image_response.json().get("message", "I couldn't process the image.")
    bot.send_message(chat_id=chat_id, text=response_text)

    # Save to Notion
    save_to_notion(f"Image Caption: {user_caption}", response_text)

def handle_unsupported_media(update: Update, context):
    chat_id = update.message.chat_id
    response_text = "I am unable to process your request."
    bot.send_message(chat_id=chat_id, text=response_text)

    # Save unsupported media info to Notion
    save_to_notion("Unsupported media received.", response_text)

@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        data = request.json

        # Set up Dispatcher to handle incoming messages
        dispatcher = Dispatcher(bot, None, workers=0)

        if "message" in data:
            update = Update.de_json(data, bot)

            if update.message.text:
                dispatcher.add_handler(MessageHandler(Filters.text, handle_text_message))
            elif update.message.photo:
                dispatcher.add_handler(MessageHandler(Filters.photo, handle_photo_message))
            else:
                dispatcher.add_handler(MessageHandler(Filters.all, handle_unsupported_media))

            dispatcher.process_update(update)

        return {"status": "ok"}
    return "Telegram bot is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
