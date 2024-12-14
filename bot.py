import logging
import asyncio
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, ContentType
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

# Create or retrieve master database
MASTER_DATABASE_ID = "15b7280d4cf580d7a8e1dd7b0bf981fa"  # To be fetched or created dynamically


async def get_or_create_master_database():
    global MASTER_DATABASE_ID
    if MASTER_DATABASE_ID:
        return MASTER_DATABASE_ID

    query = notion.search(query="Master Database", filter={"property": "object", "value": "database"})
    for result in query.get("results", []):
        if result["title"][0]["text"]["content"] == "Master Database":
            MASTER_DATABASE_ID = result["id"]
            return MASTER_DATABASE_ID

    # Create a new Master Database
    parent_page_id = "1597280d4cf580b6b54bf95cfe495487"  # Replace with your Notion Page ID
    new_db = notion.databases.create(
        parent={"type": "page_id", "page_id": parent_page_id},
        title=[{"type": "text", "text": {"content": "Master Database"}}],
        properties={
            "User ID": {"rich_text": {}},
            "Full Name": {"rich_text": {}},
            "User Database ID": {"rich_text": {}},
            "Files Uploaded": {"number": {}},
            "Storage Used": {"number": {}},
        },
    )
    MASTER_DATABASE_ID = new_db["id"]
    return MASTER_DATABASE_ID


# Get or create user-specific database
async def get_or_create_user_database(user_id: str, full_name: str):
    master_db_id = await get_or_create_master_database()

    # Check if user exists in master database
    query = notion.databases.query(
        database_id=master_db_id, filter={"property": "User ID", "rich_text": {"equals": user_id}}
    )
    results = query.get("results", [])
    if results:
        return results[0]["properties"]["User Database ID"]["rich_text"][0]["text"]["content"]

    # Create a new user-specific database
    parent_page_id = "1597280d4cf580b6b54bf95cfe495487"  # Replace with your Notion Page ID
    user_db = notion.databases.create(
        parent={"type": "page_id", "page_id": parent_page_id},
        title=[{"type": "text", "text": {"content": user_id}}],
        properties={
            "File Name": {"title": {}},
            "File ID": {"rich_text": {}},
            "Message ID": {"number": {}},
            "File Size": {"number": {}},
        },
    )

    # Add user details to master database
    notion.pages.create(
        parent={"type": "database_id", "database_id": master_db_id},
        properties={
            "User ID": {"rich_text": [{"type": "text", "text": {"content": user_id}}]},
            "Full Name": {"rich_text": [{"type": "text", "text": {"content": full_name}}]},
            "User Database ID": {"rich_text": [{"type": "text", "text": {"content": user_db["id"]}}]},
            "Files Uploaded": {"number": 0},
            "Storage Used": {"number": 0},
        },
    )

    return user_db["id"]


# Add file details to user database
async def add_file_to_user_database(user_db_id: str, file_name: str, file_id: str, msg_id: int, file_size: float):
    notion.pages.create(
        parent={"type": "database_id", "database_id": user_db_id},
        properties={
            "File Name": {"title": [{"type": "text", "text": {"content": file_name}}]},
            "File ID": {"rich_text": [{"type": "text", "text": {"content": file_id}}]},
            "Message ID": {"number": msg_id},
            "File Size": {"number": file_size},
        },
    )


# Handle file uploads
@router.message(F.content_type.in_([ContentType.DOCUMENT, ContentType.PHOTO, ContentType.VIDEO]))
async def handle_file(message: Message):
    user_id = str(message.from_user.id)
    full_name = f"{message.from_user.first_name} {message.from_user.last_name or ''}".strip()
    file = message.document or message.photo[-1] or message.video
    file_id = file.file_id
    file_name = file.file_name if hasattr(file, "file_name") else "Photo/Video"
    file_size = round(file.file_size / (1024 * 1024), 2)  # File size in MB

    # Forward file to channel
    forwarded_msg = await bot.forward_message(chat_id=CHANNEL_ID, from_chat_id=message.chat.id, message_id=message.message_id)

    # Get or create user database
    user_db_id = await get_or_create_user_database(user_id, full_name)

    # Add file details to database
    await add_file_to_user_database(user_db_id, file_name, file_id, forwarded_msg.message_id, file_size)

    await message.reply(f"File '{file_name}' uploaded successfully!")


# Handle /list command with pagination
@router.message(Command(commands=["list"]))
async def list_files(message: Message):
    user_id = str(message.from_user.id)
    user_db_id = await get_or_create_user_database(user_id, message.from_user.full_name)
    query = notion.databases.query(database_id=user_db_id)
    files = query.get("results", [])

    if not files:
        await message.reply("You don't have any files uploaded yet.")
        return

    # Generate pagination
    buttons = []
    for i, file in enumerate(files):
        file_name = file["properties"]["File Name"]["title"][0]["text"]["content"]
        file_id = file["properties"]["File ID"]["rich_text"][0]["text"]["content"]
        buttons.append(
            InlineKeyboardButton(text=file_name, callback_data=f"file:{file_id}")
        )

    markup = InlineKeyboardMarkup(row_width=1, inline_keyboard=[buttons])
    await message.reply("Your files:", reply_markup=markup)


# Handle file retrieval
@router.callback_query(F.data.startswith("file:"))
async def send_file(callback_query: CallbackQuery):
    file_id = callback_query.data.split(":")[1]
    await bot.send_document(callback_query.from_user.id, file_id)
    await callback_query.answer("File sent!")

# Main
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
