from flask import Flask, request
import requests
import threading
from notion_client import Client
import datetime

app = Flask(__name__)

# Telegram Bot Token
TELEGRAM_TOKEN = "7808291028:AAGRsVUGT2id7yrO_XaRPlYBtoYLYb_jzcg"
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

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
    requests.post(f"{TELEGRAM_API}/sendChatAction", json={"chat_id": chat_id, "action": "typing"})

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

@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        data = request.json

        if "message" in data:  # Check if it's a message
            chat_id = data["message"]["chat"]["id"]

            # Start typing status in a separate thread
            threading.Thread(target=send_typing_action, args=(chat_id,)).start()

            # Handle text message
            if "text" in data["message"]:
                user_text = data["message"]["text"]

                # Call PaxSenix GPT-4o API
                response = requests.post(TEXT_API_URL, headers={
                    "accept": "application/json",
                    "Content-Type": "application/json"
                }, json={"messages": [{"role": "user", "content": user_text}]})

                response_text = response.json().get("message", "I couldn't process your request.")
                requests.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": response_text})

                # Save chat history to Notion
                save_to_notion(user_text, response_text)

            # Handle photo message
            elif "photo" in data["message"]:
                user_caption = data["message"].get("caption", "Please Describe this Image")

                # Get the file ID of the photo
                photo_file_id = data["message"]["photo"][-1]["file_id"]  # Highest resolution
                file_response = requests.get(f"{TELEGRAM_API}/getFile?file_id={photo_file_id}")
                file_path = file_response.json()["result"]["file_path"]
                file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"

                # Call PaxSenix GeminiVision API
                image_response = requests.get(f"{IMAGE_API_URL}?text={user_caption}&url={file_url}", headers={
                    "accept": "application/json"
                })

                response_text = image_response.json().get("message", "I couldn't process the image.")
                requests.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": response_text})

                # Save image caption and response to Notion
                save_to_notion(f"Image Caption: {user_caption}", response_text)

            # Handle unsupported media
            else:
                response_text = "I am unable to process your request."
                requests.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": response_text})

                # Save unsupported media info to Notion
                save_to_notion("Unsupported media received.", response_text)

        return {"status": "ok"}
    return "Telegram bot is running!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
