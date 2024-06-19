import pyrogram
from pyrogram import Client, filters
import re
import asyncio
import aiohttp
from pymongo import MongoClient
from pyrogram.errors import FloodWait
import time

# MongoDB configuration
MONGO_URI = 'mongodb+srv://iamdaxx404:asd@mohio.1uwb6r5.mongodb.net'
client = MongoClient(MONGO_URI)
db = client['mrdaxx_scrapper_db']
cards_collection = db['cards']

def correct_padding(session_string):
    return session_string + "=" * ((4 - len(session_string) % 4) % 4)

app = pyrogram.Client(
    'mrdaxx_scrapper',
    api_id='27649783',
    api_hash='834fd6015b50b781e0f8a41876ca95c8',
    session_string=correct_padding("BQEBfSYAqGKrE3X2TyXhJQwTfbD70-BlYP6gS-TUM74yBX2nnLwT0r-pWZUn516QzjsyUfzWXibY_9h2jNc9UIEitH3aQcZhqEj4v5wQ0l0-OmAeRADY0Hicqd8zVWaoC-o9SlhZmbE1xA9JWQVTMC_FF6EG3Xx1K1pkRwW-0NkA7uvBxV-q3uaLzSdy2gplOz0KlGXOqITpruRDfNcPDBjQjgmguH_A-7Q6C0oyqZ8l-k1W42JrR9f3aEx5p8ym7v2P8Wwo4X2KmjFL2yjphY8E-A04UjCH0KjQeudADe8bSry8MGvJ5JN142pEz4QxMEr8IH-UdwdGj6IA-3qAnBEW4HeulgAAAAGw_lmDAA")  # Ensure correct padding
)

BIN_API_URL = 'https://astroboyapi.com/api/bin.php?bin={}'

def filter_cards(text):
    regex = r'\d{16}\D*\d{3}'
    return re.findall(regex, text)

async def bin_lookup(bin_number):
    bin_info_url = BIN_API_URL.format(bin_number)
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        async with session.get(bin_info_url) as response:
            if response.status == 200:
                try:
                    return await response.json()
                except aiohttp.ContentTypeError:
                    return None
            return None

async def send_message_with_retry(Client, chat_id, text, retries=5):
    attempt = 0
    while attempt < retries:
        try:
            await Client.send_message(chat_id=chat_id, text=text)
            return
        except FloodWait as e:
            print(f"FloodWait error: sleeping for {e.value} seconds")
            await asyncio.sleep(e.value)
            attempt += 1
        except Exception as e:
            print(f"Unexpected error: {e}")
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
            attempt += 1

async def process_card(Client, card_info):
    bin_number = card_info[:6]
    bin_info = await bin_lookup(bin_number)
    if bin_info:
        brand = bin_info.get("brand", "N/A")
        card_type = bin_info.get("type", "N/A")
        level = bin_info.get("level", "N/A")
        bank = bin_info.get("bank", "N/A")
        country = bin_info.get("country_name", "N/A")
        country_flag = bin_info.get("country_flag", "")

        formatted_message = (
            "┏━━━━━━━⍟\n"
            "┃𝖡𝖱𝖠𝖨𝖭𝖳𝖱𝖤𝖤 𝖠𝖴𝖳𝖧 𝟓$ ✅\n"
            "┗━━━━━━━━━━━⊛\n\n"
            f"𖠁𝖢𝖠𝖱𝖣 ➔ <code>{card_info}</code>\n\n"
            f"𖠁𝖲𝖳𝖠𝖳𝖴𝖲 ➔ <b>Approved! ✅</b>\n\n"
            f"𖠁𝖡𝖨𝖭 ➔ <b>{brand}, {card_type}, {level}</b>\n\n"
            f"𖠁𝖡𝖠𝖭𝖪 ➔ <b>{bank}</b>\n\n"
            f"𖠁𝖢𝖮𝖴𝖭𝖳𝖱𝖸 ➔ <b>{country}, {country_flag}</b>\n\n"
            "𖠁𝖢𝖱𝖤𝖠𝖳𝖮𝖱 ➔ <b>๏─𝙂𝘽𝙋─๏</b>"
        )

        await send_message_with_retry(Client, '-1002222638488', formatted_message)

        # Save card info to MongoDB to prevent duplicate sending
        cards_collection.insert_one({"card_info": card_info})

async def approved(Client, message):
    try:
        if re.search(r'(Approved!|Charged|authenticate_successful|𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱|APPROVED|New Cards Found By JennaScrapper|ꕥ Extrap [☭]|み RIMURU SCRAPE by|Approved) ✅', message.text):
            filtered_card_info = filter_cards(message.text)
            if not filtered_card_info:
                return

            tasks = []
            for card_info in filtered_card_info:
                if not cards_collection.find_one({"card_info": card_info}):
                    tasks.append(process_card(Client, card_info))

            await asyncio.gather(*tasks)
    except Exception as e:
        print(e)

@app.on_message(filters.text)
async def astro(Client, message):
    if message.text:
        await approved(Client, message)

app.run()
