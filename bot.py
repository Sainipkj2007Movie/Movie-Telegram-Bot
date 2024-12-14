from telethon import TelegramClient, events
from telethon.tl.types import InputPeerUser
import asyncio

# Bot Token for your Telegram bot
TELEGRAM_TOKEN = "7808291028:AAGRsVUGT2id7yrO_XaRPlYBtoYLYb_jzcg"
# Admin Bot's API ID and Hash
API_ID = '24673538'  # Replace with your API ID
API_HASH = '555639745e6ceee1ae3797866136998f'  # Replace with your API Hash

# The ID of the second bot (to forward messages to)
OTHER_BOT_ID = 2138323286  # Replace with the second bot ID

# Create the Telegram client
client = TelegramClient('bot', API_ID, API_HASH)

# Function to forward messages and handle replies
@client.on(events.NewMessage)
async def handler(event):
    user_message = event.message
    user = event.sender_id  # Get the user who sent the message

    # Forward the received message to the other bot
    # If the message is a text message:
    if user_message.text:
        forwarded_message = await client.send_message(OTHER_BOT_ID, user_message.text)
    # If the message is a file:
    elif user_message.media:
        forwarded_message = await client.send_file(OTHER_BOT_ID, user_message.media)

    # Wait for the reply from the second bot
    @client.on(events.NewMessage(from_users=OTHER_BOT_ID))
    async def reply_handler(reply_event):
        # Check if the reply is from the second bot
        reply = reply_event.message
        # Forward the reply back to the user
        await client.send_message(user, reply.text or "File received and forwarded.")  # Handle text and media

        # Optionally, if the second bot replies with a file
        if reply.media:
            await client.send_file(user, reply.media)

        # Unregister the reply handler after sending the reply
        reply_handler._handler.remove()

# Start the client and run the bot
client.start(bot_token=TELEGRAM_TOKEN)

print("Bot is running...")

# Keep the bot running
client.run_until_disconnected()
