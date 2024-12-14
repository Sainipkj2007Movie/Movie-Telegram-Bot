import logging
import asyncio
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile, ContentType
from notion_client import Client
import os

# Environment Variables
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
CHANNEL_ID = -1002403053494  # Replace with your channel ID

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# Initialize Notion client
notion = Client(auth=NOTION_TOKEN)

# Function to create or fetch a Notion database for the user
async def get_or_create_database(user_id: str):
    query = notion.search(query=user_id, filter={"property": "object", "value": "database"})

    # If database exists, return its ID
    for result in query.get("results", []):
        if result["title"][0]["text"]["content"] == user_id:
            return result["id"]

    # If no database exists, create a new one
    parent_page_id = "1597280d4cf580b6b54bf95cfe495487"  # Replace with your Notion Page ID
    new_db = notion.databases.create(
        parent={"type": "page_id", "page_id": parent_page_id},
        title=[{"type": "text", "text": {"content": user_id}}],
        properties={
            "File Name": {"title": {}},
            "Message ID": {"number": {}},
            "File ID": {"rich_text": {}},
        },
    )
    return new_db["id"]

# Function to add file details to Notion database
async def add_file_to_database(database_id: str, file_name: str, msg_id: int, file_id: str):
    notion.pages.create(
        parent={"type": "database_id", "database_id": database_id},
        properties={
            "File Name": {"title": [{"type": "text", "text": {"content": file_name}}]},
            "Message ID": {"number": msg_id},
            "File ID": {"rich_text": [{"type": "text", "text": {"content": file_id}}]},
        },
    )

# Handler for file uploads
@router.message(F.content_type.in_([ContentType.DOCUMENT, ContentType.PHOTO, ContentType.VIDEO]))
async def handle_file(message: Message):
    user_id = str(message.from_user.id)
    file_id = message.document.file_id if message.document else message.photo[-1].file_id if message.photo else message.video.file_id
    file_name = message.document.file_name if message.document else "Photo" if message.photo else "Video"

    # Forward file to the channel
    forwarded_msg = await bot.forward_message(chat_id=CHANNEL_ID, from_chat_id=message.chat.id, message_id=message.message_id)
    
    # Get or create the database for the user
    database_id = await get_or_create_database(user_id)

    # Add file details to the database
    await add_file_to_database(database_id, file_name, forwarded_msg.message_id, file_id)

    await message.reply(f"Your file '{file_name}' has been uploaded and saved to Notion.")

# Handler for /list command
@router.message(Command(commands=["list"]))
async def list_files(message: Message):
    user_id = str(message.from_user.id)
    database_id = await get_or_create_database(user_id)

    # Query all pages in the user's database
    query = notion.databases.query(database_id=database_id)
    results = query.get("results", [])

    if not results:
        await message.reply("You don't have any files saved yet.")
        return

    file_list = "\n".join([f"{i + 1}. {page['properties']['File Name']['title'][0]['text']['content']}" for i, page in enumerate(results)])
    await message.reply(f"Your files:\n{file_list}")

# Main function to start the bot
async def main():
    try:
        logging.info("Starting bot...")
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
