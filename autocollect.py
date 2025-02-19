import os
import logging
import imagehash
from PIL import Image
import asyncio
from concurrent.futures import ThreadPoolExecutor
from telethon import TelegramClient, events

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set to DEBUG to capture all levels of logs

# File handler
file_handler = logging.FileHandler('bot.log', mode='a')  # Append mode
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Replace these with your API credentials
api_id = ''
api_hash = ''
phone_number = '+'

# Create the client instance
client = TelegramClient('@CollectYourPlayerxBot', api_id, api_hash)

# Define the group ID or username (replace with actual group info)
group = -

# Define the target caption
target_caption = "🔥 ʟᴏᴏᴋ ᴀɴ ᴏɢ ᴘʟᴀʏᴇʀ ᴊᴜꜱᴛ ᴀʀʀɪᴠᴇᴅ ᴄᴏʟʟᴇᴄᴛ ʜɪᴍ ᴜꜱɪɴɢ /ᴄᴏʟʟᴇᴄᴛ ɴᴀᴍᴇ"

# Path to player images directory
player_images_dir = "C:\\Users\\Dell\\Downloads\\Telegram Desktop\\Collection"

# Dictionary of player image hashes
player_image_hashes = {}

# Preload player images and cache hashes with reduced resolution
def preload_player_images(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.jpg'):
            player_name = os.path.splitext(filename)[0]
            image_path = os.path.join(directory, filename)

            # Reduce resolution for faster processing
            image = Image.open(image_path).resize((32, 32))  # Reduced resolution

            # Cache the hash
            player_image_hashes[player_name] = imagehash.average_hash(image)
            logger.info(f"Preloaded {player_name}: {image_path}")

# Preload images at startup
preload_player_images(player_images_dir)

# Function to collect the player
async def collect_player(event, player_name):
    await event.reply(f"/collect {player_name}")
    logger.info(f"Collected player: {player_name}")

# Function to compare images using cached hashes
def compare_images(image_path):
    try:
        image = Image.open(image_path).resize((32, 32))  # Reduced resolution
        hash1 = imagehash.average_hash(image)
        for player_name, hash2 in player_image_hashes.items():
            if hash1 - hash2 < 5:  # Adjust threshold as needed
                return player_name
    except Exception as e:
        logger.error(f"Error comparing images: {e}")
    return None

# Function to handle comparisons in parallel
async def process_comparisons(event, image_path):
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=30) as executor:  # Experiment with max_workers
        player_name = await loop.run_in_executor(executor, compare_images, image_path)
        if player_name:
            await collect_player(event, player_name)
        else:
            logger.error("No matching player image found.")

@client.on(events.NewMessage(chats=group))
async def handler(event):
    if event.photo:
        caption = event.text

        if caption and target_caption in caption:
            image_path = 'received_image.jpg'
            try:
                await event.download_media(file=image_path)

                # Process comparisons in parallel
                await process_comparisons(event, image_path)

            except Exception as e:
                logger.error(f"Error processing event: {e}")

async def main():
    try:
        await client.start(phone_number)
        await client.run_until_disconnected()
    except Exception as e:
        logger.error(f"Error starting the client: {e}")

if __name__ == '__main__':
    client.loop.run_until_complete(main())
