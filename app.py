from flask import Flask, request
import requests

app = Flask(__name__)

# Telegram bot token and API URL
TELEGRAM_TOKEN = "7808291028:AAGRsVUGT2id7yrO_XaRPlYBtoYLYb_jzcg"
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Datamuse API URL
DATAMUSE_API = "https://api.datamuse.com/words?ml="

@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        data = request.json

        # Handle inline query
        if "inline_query" in data:
            inline_query_id = data["inline_query"]["id"]
            query = data["inline_query"]["query"]

            # Fetch data from Datamuse API
            datamuse_response = requests.get(DATAMUSE_API + query)
            words = datamuse_response.json()

            # Prepare inline results
            results = []
            for word in words[:10]:  # Top 10 results
                results.append({
                    "type": "article",
                    "id": word["word"],
                    "title": word["word"],
                    "input_message_content": {
                        "message_text": f"Word: {word['word']}"
                    }
                })

            # Send inline query results
            requests.post(f"{TELEGRAM_API}/answerInlineQuery", json={
                "inline_query_id": inline_query_id,
                "results": results
            })

        # Handle normal messages
        elif "message" in data:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"]["text"]
            response_text = f"You said: {text}"

            # Send a reply
            requests.post(f"{TELEGRAM_API}/sendMessage", json={
                "chat_id": chat_id,
                "text": response_text
            })

        return {"status": "ok"}
    return "Telegram bot is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
