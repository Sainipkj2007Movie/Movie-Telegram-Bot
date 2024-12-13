from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Telegram bot token and API URL
TELEGRAM_TOKEN = "7808291028:AAGRsVUGT2id7yrO_XaRPlYBtoYLYb_jzcg"
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Datamuse API URL
DATAMUSE_API = "https://api.datamuse.com/words?ml="

# Admin chat ID
ADMIN_CHAT_ID = 6150091802

@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        # Check if the request is JSON
        if not request.is_json:
            return jsonify({"error": "Invalid request, expecting JSON"}), 400
        
        data = request.json
        
        # Send the received data to the admin chat (user 6150091802)
        try:
            requests.post(f"{TELEGRAM_API}/sendMessage", json={
                "chat_id": ADMIN_CHAT_ID,
                "text": f"Received data: {data}"
            })
        except Exception as e:
            print(f"Error sending data to admin: {e}")
        
        # Handle inline query
        if "inline_query" in data:
            inline_query_id = data["inline_query"]["id"]
            query = data["inline_query"]["query"]

            # Fetch data from Datamuse API
            try:
                datamuse_response = requests.get(DATAMUSE_API + query)
                datamuse_response.raise_for_status()  # Raise an exception for HTTP errors
                words = datamuse_response.json()
            except requests.exceptions.RequestException as e:
                print(f"Error fetching data from Datamuse API: {e}")
                words = []

            # Prepare inline query results
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

            # Send a reply to the original sender
            requests.post(f"{TELEGRAM_API}/sendMessage", json={
                "chat_id": chat_id,
                "text": response_text
            })

        return jsonify({"status": "ok"}), 200
    
    return "Telegram bot is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
