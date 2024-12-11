from flask import Flask, request
import requests

app = Flask(__name__)

TELEGRAM_TOKEN = "7808291028:AAGRsVUGT2id7yrO_XaRPlYBtoYLYb_jzcg"
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
ADMIN_ID = 5943119285  # Admin ID
CHANNEL_ID = -1002403053494  # Private Channel ID

# Store current admin video state
admin_state = {}

@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        data = request.json
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text")
        user_id = data["message"]["from"]["id"]

        # Admin Check: If the user is the admin
        if user_id == ADMIN_ID:
            if text == "/start":
                # Send greeting to admin
                response_text = "Hello My Dear Friend. You are My admin. How are you My God. Do you want to upload a movie? Please Send a video or any File."
                requests.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": response_text})

            elif "video" in data["message"]:
                # If admin sends a video, upload to the channel and get message ID
                video_file_id = data["message"]["video"]["file_id"]
                message_id = send_video_to_channel(video_file_id)

                if message_id:
                    # Store the message ID for further use
                    admin_state[user_id] = {"channel_message_id": message_id, "waiting_for_movie_name": True}
                    response_text = "It is looking nice movie! My God. Please provide this movie name."
                    requests.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": response_text})
                else:
                    response_text = "Failed to upload the video to the channel. Please try again."
                    requests.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": response_text})

            elif user_id in admin_state and admin_state[user_id].get("waiting_for_movie_name"):
                # Handle movie name input from admin
                movie_name = text
                admin_state[user_id]["movie_name"] = movie_name
                admin_state[user_id]["waiting_for_movie_name"] = False
                admin_state[user_id]["waiting_for_date"] = True

                response_text = f"Your Provided Movie Name - {movie_name}, Now provide the Date (DD/MM/YYYY) when it was released."
                requests.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": response_text})

            elif user_id in admin_state and admin_state[user_id].get("waiting_for_date"):
                # Validate and handle movie release date input from admin
                if validate_date_format(text):
                    release_date = text
                    admin_state[user_id]["release_date"] = release_date
                    send_movie_details_to_google_script(admin_state[user_id])

                    # Reset state after sending details
                    del admin_state[user_id]
                    response_text = "Movie details submitted successfully!"
                    requests.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": response_text})
                else:
                    response_text = "Invalid date format. Please provide the date in DD/MM/YYYY format."
                    requests.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": response_text})

            else:
                # If admin sends any other video before providing all details, reject the video
                if "video" in data["message"]:
                    response_text = "Please complete the details for the previous video before uploading a new one. Or type /cancel to cancel."
                    requests.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": response_text})

        else:
            # Non-admin user message handling
            response_text = "You are not authorized to interact with this bot."
            requests.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": response_text})

        return {"status": "ok"}
    return "Telegram bot is running!"

def send_video_to_channel(file_id):
    """Send video to the private channel and return the channel message ID."""
    response = requests.post(f"{TELEGRAM_API}/sendVideo", json={"chat_id": CHANNEL_ID, "video": file_id})
    if response.ok:
        result = response.json()
        return result["result"]["message_id"]
    return None

def validate_date_format(date_str):
    """Validate date format as DD/MM/YYYY."""
    try:
        from datetime import datetime
        datetime.strptime(date_str, "%d/%m/%Y")
        return True
    except ValueError:
        return False

def send_movie_details_to_google_script(movie_details):
    """Send movie details to Google Script via POST request."""
    movie_data = {
        "Movie Name": movie_details["movie_name"],
        "Massage Id": str(movie_details["channel_message_id"]),
        "Date Added": movie_details["release_date"]
    }
    google_script_url = "https://script.google.com/macros/s/AKfycbzixknSdjyAV62WD95udegTHZsYMC27cPQnB0FqysnIjAWV2qvNRJPwnpFho8TOcCXf/exec"
    requests.post(google_script_url, json=movie_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
