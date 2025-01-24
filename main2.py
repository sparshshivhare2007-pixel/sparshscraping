import asyncio
import re
from typing import List, Tuple, Optional, Dict, Pattern
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message

# Configuration
API_ID = 27649783
API_HASH = '834fd6015b50b781e0f8a41876ca95c8'
BOT_NAME = 'mrdaxx_scrapper'
TARGET_CHANNEL = '@vclubhits'
BOT_CREATOR = '@vclubdrop'
BIN_API_URL = 'https://astroboyapi.com/api/bin.php?bin={}'
CARD_REGEX = r'\b(\d{15,16})\D*(\d{2})\D*(\d{2,4})\D*(\d{3,4})\b'
APPROVED_PATTERNS = [
    'Approved!', 'MASTERCARD', 'VISA', '✺ Extrap', '#bin', 
    'Charged', 'authenticate_successful', '𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱',
    'APPROVED', '🔥', 'New Cards Found By DaxxScrapper',
    'ꕥ Extrap [☭]', 'み RIMURU SCRAPE by', 'Approved ✅'
]

# Your string session here
STRING_SESSION = "YOUR_STRING_SESSION_HERE"

class CardProcessor:
    @staticmethod
    def filter_cards(text: str) -> List[Tuple[str, str, str, str]]:
        """Extract card information from text using regex."""
        try:
            matches = re.findall(CARD_REGEX, text)
            return matches
        except Exception as e:
            print(f"Error in filter_cards: {e}")
            return []

    @staticmethod
    async def bin_lookup(bin_number: str) -> Optional[Dict]:
        """Perform BIN lookup for a card number."""
        bin_info_url = BIN_API_URL.format(bin_number)
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(bin_info_url) as response:
                    if response.status == 200:
                        return await response.json()
                    print(f"BIN lookup failed with status {response.status}")
            except Exception as e:
                print(f"Error during BIN lookup: {e}")
        return None

    @staticmethod
    def format_message(
        card_data: Tuple[str, str, str, str],
        bin_info: Dict
    ) -> str:
        """Format card information into a Telegram message."""
        card_number, month, year, cvv = card_data
        
        return (
            "┏━━━━━━━⍟\n"
            "┃**˹CHARGE˼˹1$˼**\n"
            "┗━━━━━━━━━━━⊛\n\n"
            "**⦿ EXTRAP**  ➠\n"
            f"`{card_number[:8]}|{month}|{year}|xxx`\n"
            f"`{card_number[:12]}|{month}|{year}|xxx`\n\n"
            f"**⦿ 𝖢𝖠𝖱𝖣** ➠ <code>{card_number}|{month}|{year}|{cvv}</code>\n"
            f"**⦿ 𝖲𝖳𝖠𝖳𝖴𝖲** ➠ <b>STRIPE CHARGE 1$ </b>\n"
            f"**⦿ 𝖡𝖨𝖭** ➠ <b>{bin_info.get('brand', 'N/A')}, {bin_info.get('type', 'N/A')}, {bin_info.get('level', 'N/A')}</b>\n"
            f"**⦿ 𝖡𝖠𝖭𝖪** ➠ <b>{bin_info.get('bank', 'N/A')}</b>\n"
            f"**⦿ 𝖢𝖮𝖴𝖭𝖳𝖱𝖸** ➠ <b>{bin_info.get('country_name', 'N/A')}, {bin_info.get('country_flag', '')}</b>\n"
            "**⦿ 𝖢𝖱𝖤𝖠𝖳𝖮𝖱** ➠ <b>@vclubdrop</b>"
        )

class MessageHandler:
    def __init__(self):
        self.card_processor = CardProcessor()
        self.approved_pattern = self._compile_approved_pattern()

    @staticmethod
    def _compile_approved_pattern() -> Pattern:
        """Compile regex pattern for approved messages."""
        pattern = '|'.join(map(re.escape, APPROVED_PATTERNS))
        return re.compile(f'({pattern})')

    async def process_message(self, client: Client, message: Message) -> None:
        """Process incoming messages and forward valid card information."""
        try:
            if not message.text or not self.approved_pattern.search(message.text):
                return

            card_matches = self.card_processor.filter_cards(message.text)
            if not card_matches:
                return

            for card in card_matches:
                try:
                    bin_info = await self.card_processor.bin_lookup(card[0][:6])
                    if not bin_info:
                        continue

                    formatted_msg = self.card_processor.format_message(card, bin_info)
                    await client.send_message(
                        chat_id=TARGET_CHANNEL,
                        text=formatted_msg
                    )
                except Exception as e:
                    print(f"Error processing card: {e}")

        except Exception as e:
            print(f"Error in message processing: {e}")

class CardScraperBot:
    def __init__(self):
        self.client = Client(
            name="bot",
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=STRING_SESSION
        )
        self.message_handler = MessageHandler()

    async def start(self):
        """Start the bot and register message handlers."""
        try:
            @self.client.on_message(filters.text & (filters.group | filters.channel))
            async def handle_message(client, message):
                await self.message_handler.process_message(client, message)

            print("Starting bot...")
            await self.client.start()
            print("Bot is running...")
            await self.client.idle()

        except Exception as e:
            print(f"Error starting bot: {e}")
        finally:
            await self.client.stop()

if __name__ == "__main__":
    bot = CardScraperBot()
    asyncio.run(bot.start())
