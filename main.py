import pyrogram
from pyrogram import Client, filters
import re
import aiohttp

# Telegram bot setup
app = Client(
    'mrdaxx_scrapper',
    api_id=27649783,
    api_hash='834fd6015b50b781e0f8a41876ca95c8'
)

# API for BIN lookup
BIN_API_URL = 'https://astroboyapi.com/api/bin.php?bin={}'

def filter_cards(text):
    try:
        regex = r'\b\d{15,16}\D*\d{2}\D*\d{2,4}\D*\d{3,4}\b'
        matches = re.findall(regex, text)
        print(f"Filtered cards: {matches}")
        return matches
    except Exception as e:
        print(f"Error in filter_cards: {e}")
        return []

async def bin_lookup(bin_number):
    bin_info_url = BIN_API_URL.format(bin_number)
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(bin_info_url) as response:
                if response.status == 200:
                    print(f"BIN lookup successful for {bin_number}")
                    return await response.json()
                else:
                    print(f"BIN lookup failed with status {response.status} for {bin_number}")
        except Exception as e:
            print(f"Error during BIN lookup for {bin_number}: {e}")
    return None

async def approved(client_instance, message):
    try:
        if re.search(r'(Approved!|Charged|authenticate_successful|𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱|APPROVED|New Cards Found By DaxxScrapper|ꕥ Extrap [☭]|み RIMURU SCRAPE by|Approved) ✅', message.text):
            filtered_card_info = filter_cards(message.text)
            if not filtered_card_info:
                print("No valid card information found in message.")
                return

            for card_info in filtered_card_info:
                try:
                    # Perform BIN lookup
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

                        # Send message to Telegram channel
                        await client_instance.send_message(chat_id='@CHARGECCDROP', text=formatted_message)
                        print("Message sent to channel successfully.")
                except Exception as e:
                    print(f"Error processing card info {card_info}: {e}")
    except Exception as e:
        print(f"An error occurred in approved function: {e}")

@app.on_message(filters.text & filters.all)
async def forward_all(client_instance, message):
    try:
        print("Forwarding message from joined group.")
        await approved(client_instance, message)
    except Exception as e:
        print(f"Error in forward_all function: {e}")

try:
    print("Starting bot...")
    app.run()
except Exception as e:
    print(f"Error starting the bot: {e}")
    
