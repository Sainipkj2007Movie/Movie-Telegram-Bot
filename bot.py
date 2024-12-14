from flask import Flask, request
import requests
from telethon import TelegramClient

app = Flask(__name__)

# Your Telegram Bot Token
TELEGRAM_TOKEN = ""7808291028:AAGRsVUGT2id7yrO_XaRPlYBtoYLYb_jzcg
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Admin Bot's API ID and Hash
API_ID = '24673538'  # Replace with your API ID
API_HASH = '555639745e6ceee1ae3797866136998f'  # Replace with your API Hash
ADMIN_CHAT_ID = '5943119285'  # Replace with your admin's chat ID

# The ID of the other bot (2138323286)
OTHER_BOT_ID = 2138323286

# Create the Telegram client
client = TelegramClient('bot', API_ID, API_HASH)

@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        data = request.json
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]

        # Sending the reply back to the user
        response_text = f"You said: {text}"
        requests.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": response_text})
        
        # Send a message to the other bot (2138323286)
        async def send_to_other_bot():
            await client.send_message(OTHER_BOT_ID, f"Message received from chat {chat_id}: {text}")
        
        # Start the client to send the message
        client.loop.run_until_complete(send_to_other_bot())

        # Send a notification to the admin bot
        async def send_admin_notification():
            await client.send_message(ADMIN_CHAT_ID, f"New message received from {chat_id}: {text}")
        
        # Start the client to send the admin notification
        client.loop.run_until_complete(send_admin_notification())

        return {"status": "ok"}
    
    return "Telegram bot is running!"

if __name__ == "__main__":
    # Start the client and run the Flask app
    client.start()
    app.run(host="0.0.0.0", port=5000)
