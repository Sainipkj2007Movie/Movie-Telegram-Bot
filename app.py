from flask import Flask, request
import requests

app = Flask(__name__)

# Bot ke liye token aur API URL
TELEGRAM_TOKEN = "7808291028:AAGRsVUGT2id7yrO_XaRPlYBtoYLYb_jzcg"
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Private channel video file_id
VIDEO_FILE_ID = "BAACAgEAAxkBAAIBB2dcZOLbovWF0VBR-o9uhWz92iLOAAKcBQACcA4RR6-WKst4MQMkNgQ"  # Replace with actual video file_id

@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        data = request.json

        # Handle inline query
        if "inline_query" in data:
            inline_query_id = data["inline_query"]["id"]
            query = data["inline_query"]["query"]

            # Check if the user typed "video"
            if query.lower() == "video":  # Matching the keyword "video"
                # Prepare inline query result with video file_id
                results = [
                    {
                        "type": "video",
                        "id": "unique-id-1",
                        "video_file_id": VIDEO_FILE_ID,  # Use the file ID of the video from the channel
                        "title": "Sample Video",
                        "caption": "Here is the video from the private channel.",
                    }
                ]

                # Send the inline query result
                requests.post(f"{TELEGRAM_API}/answerInlineQuery", json={
                    "inline_query_id": inline_query_id,
                    "results": results
                })

        return {"status": "ok"}
    return "Telegram bot is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
