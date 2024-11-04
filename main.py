import os
import pyrogram
from pyrogram import Client, filters
import re
import requests  # Using requests instead of aiohttp
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram bot setup using environment variables
app = Client(
    'mrdaxx_scrapper',
    api_id=os.getenv('API_ID'),  # Use environment variables
    api_hash=os.getenv('API_HASH')
)

# API for BIN lookup
BIN_API_URL = 'https://bins.antipublic.cc/bins/{}'

def filter_cards(text):
    try:
        regex = r'\b(\d{15,16})\D*(\d{2})\D*(\d{2,4})\D*(\d{3,4})\b'
        matches = re.findall(regex, text)
        logger.info(f"Filtered cards: {matches}")
        return matches
    except Exception as e:
        logger.error(f"Error in filter_cards: {e}")
        return []

def bin_lookup(bin_number):
    bin_info_url = BIN_API_URL.format(bin_number)
    try:
        response = requests.get(bin_info_url)
        if response.status_code == 200:
            logger.info(f"BIN lookup successful for {bin_number}")
            return response.json()
        else:
            logger.warning(f"BIN lookup failed with status {response.status_code} for {bin_number}")
    except Exception as e:
        logger.error(f"Error during BIN lookup for {bin_number}: {e}")
    return None

async def approved(client_instance, message):
    try:
        if re.search(r'(Approved!|Charged|authenticate_successful|𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱|APPROVED|🔥|New Cards Found By DaxxScrapper|ꕥ Extrap [☭]|み RIMURU SCRAPE by|Approved) ✅', message.text):
            filtered_card_info = filter_cards(message.text)
            if not filtered_card_info:
                logger.info("No valid card information found in message.")
                return

            for card in filtered_card_info:
                try:
                    card_number, month, year, cvv = card
                    bin_number = card_number[:6]
                    bin_info = bin_lookup(bin_number)  # Synchronous call to new API
                    if bin_info:
                        brand = bin_info.get("brand", "N/A")
                        card_type = bin_info.get("type", "N/A")
                        level = bin_info.get("level", "N/A")
                        bank = bin_info.get("bank", "N/A")
                        country = bin_info.get("country_name", "N/A")
                        country_flag = bin_info.get("country_flag", "")

                        formatted_message = (
                            "┏━━━━━━━⍟\n"
                            "┃**#CHARGE1$**\n"
                            "┗━━━━━━━━━━━⊛\n\n"
                            "**⦿ EXTRAP**  ➠\n"
                            f"`{bin_number}|{month}|{year}|xxx`\n"
                            f"`{card_number[:8]}|{month}|{year}|xxx`\n\n"
                            f"**⦿ 𝖢𝖠𝖱𝖣** ➠ <code>{card_number}|{month}|{year}|{cvv}</code>\n"
                            f"**⦿ 𝖲𝖳𝖠𝖳𝖴𝖲** ➠ <b>STRIPE CHARGE 1$ </b>\n"
                            f"**⦿ 𝖡𝖨𝖭** ➠ <b>{brand}, {card_type}, {level}</b>\n"
                            f"**⦿ 𝖡𝖠𝖭𝖪** ➠ <b>{bank}</b>\n"
                            f"**⦿ 𝖢𝖮𝖴𝖭𝖳𝖱𝖸** ➠ <b>{country}, {country_flag}</b>\n"
                            "**⦿ 𝖢𝖱𝖤𝖠𝖳𝖮𝖱** ➠ <b>@Vclubcharge</b>"
                        )

                        await client_instance.send_message(chat_id='@CHARGECCDROP', text=formatted_message)
                        logger.info("Message sent to channel successfully.")
                except Exception as e:
                    logger.error(f"Error processing card info {card}: {e}")
    except Exception as e:
        logger.error(f"An error occurred in approved function: {e}")

@app.on_message(filters.text & (filters.group | filters.channel | filters.all))
async def forward_all(client_instance, message):
    try:
        logger.info("Forwarding message from joined group or channel.")
        await approved(client_instance, message)
    except Exception as e:
        logger.error(f"Error in forward_all function: {e}")

if __name__ == "__main__":
    try:
        logger.info("Starting bot...")
        app.run()
    except Exception as e:
        logger.error(f"Error starting the bot: {e}")
