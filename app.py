from flask import Flask, request
import requests

app = Flask(__name__)

# Telegram bot token and API URL
TELEGRAM_TOKEN = "7808291028:AAGRsVUGT2id7yrO_XaRPlYBtoYLYb_jzcg"
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Video File ID
VIDEO_FILE_ID = "BAACAgEAAxkBAAIBB2dcZOLbovWF0VBR-o9uhWz92iLOAAKcBQACcA4RR6-WKst4MQMkNgQ"

@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        data = request.json

        # Handle inline query
        if "inline_query" in data:
            inline_query_id = data["inline_query"]["id"]
            query = data["inline_query"]["query"]

            # Check if the query is "A" and respond with the video
            if query.lower() == "a":
                results = [{
                    "type": "video",
                    "id": "1",
                    "title": "A murari",  # Video title
                    "video_file_id": VIDEO_FILE_ID,
                    "input_message_content": {
                        "message_text": "Watch 'A Murari' Video"
                    }
                }]

                # Send inline query result with video
                requests.post(f"{TELEGRAM_API}/answerInlineQuery", json={
                    "inline_query_id": inline_query_id,
                    "results": results
                })

        return {"status": "ok"}
    return "Telegram bot is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
