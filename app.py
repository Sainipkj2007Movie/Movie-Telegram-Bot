from flask import Flask, request
import requests

app = Flask(__name__)

TELEGRAM_TOKEN = "7808291028:AAGRsVUGT2id7yrO_XaRPlYBtoYLYb_jzcg"
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
ADMIN_ID = 5943119285  # Admin ID
CHANNEL_ID = -1002403053494  # Private Channel ID
MOVIE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzixknSdjyAV62WD95udegTHZsYMC27cPQnB0FqysnIjAWV2qvNRJPwnpFho8TOcCXf/exec"

@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        data = request.json

        # Handle inline queries
        if "inline_query" in data:
            inline_query_id = data["inline_query"]["id"]
            query_text = data["inline_query"]["query"].strip().lower()
            handle_inline_query(inline_query_id, query_text)
            return {"status": "ok"}

        # Handle callback query for selected movie
        if "callback_query" in data:
            callback_query = data["callback_query"]
            callback_data = callback_query["data"]
            chat_id = callback_query["from"]["id"]
            handle_movie_selection(chat_id, callback_data)
            return {"status": "ok"}

        return {"status": "ok"}
    return "Telegram bot is running!"

def send_video_to_channel(file_id):
    """Send video to the private channel and return the channel message ID."""
    response = requests.post(f"{TELEGRAM_API}/sendVideo", json={"chat_id": CHANNEL_ID, "video": file_id})
    if response.ok:
        result = response.json()
        return result["result"]["message_id"]
    return None

def handle_inline_query(inline_query_id, query_text):
    """Handle inline query to search movies."""
    response = requests.get(MOVIE_SCRIPT_URL)
    movies = response.json()

    # Filter and sort movies based on the query
    if query_text:
        filtered_movies = [
            movie for movie in movies if query_text in movie["Movie Name"].lower()
        ]
        filtered_movies.sort(key=lambda x: x["Movie Name"].lower().startswith(query_text), reverse=True)
    else:
        filtered_movies = movies  # Show all movies if no query

    # Prepare results for Telegram inline query
    results = []
    for idx, movie in enumerate(filtered_movies):
        results.append({
            "type": "article",
            "id": str(idx),
            "title": movie["Movie Name"],
            "description": f"Released: {movie['Date Added']}",
            "input_message_content": {
                "message_text": f"Fetching the movie..."
            },
    try:
        # Forward the movie from the channel to the user
        response = requests.post(f"{TELEGRAM_API}/forwardMessage", json={
            "chat_id": chat_id,
            "from_chat_id": CHANNEL_ID,
            "message_id": int(message_id)
        })

        if response.ok:
            requests.post(f"{TELEGRAM_API}/sendMessage", json={
                "chat_id": chat_id,
                "text": "Movie has been sent successfully!"
            })
        else:
            requests.post(f"{TELEGRAM_API}/sendMessage", json={
                "chat_id": chat_id,
                "text": "Failed to fetch the movie. Please try again later."
            })
    except Exception as e:
        requests.post(f"{TELEGRAM_API}/sendMessage", json={
            "chat_id": chat_id,
            "text": f"Error: {str(e)}"
        })
    # Send results to Telegram
    requests.post(f"{TELEGRAM_API}/answerInlineQuery", json={
        "inline_query_id": inline_query_id,
        "results": results
    })

def handle_movie_selection(chat_id, message_id):
    """Forward the selected movie to the user."""
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
