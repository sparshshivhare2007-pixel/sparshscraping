import pyrogram
from pyrogram import Client, filters
import re
import asyncio
import aiohttp

app = pyrogram.Client(
    'jetix_scrapper',
    api_id='6134343',
    api_hash='344493a60221b6483e47b00ff1461708',
    session_string='''
BQGoLIMAOKXVTjaGOZN_8kShQdKccRd7HA-44GV5eLHHMW-x5wkMEWQHeNeymWRAp-Zml2tZZ8OjP8s-1_eLLKZiJTud9Nm8KO6iBNw_n91qB0tob5XfHcP9VRl1Yd97cCXOMv-wiQNNEN_APBKTGTrSdoEJxyv7RymmlhBSvmxmnIaewzSNR9rUE7SCojVWYskW01O7ootmaa41nPSJgFjfAn0bUGRI838LlbkDpxVuBqb83BTTunwBNlddBXmm10dm2aw7CaVf9JrCyn_X9dhB0YGoanFGqXFYGKpj7nshJ4djVN8MHtLRB3oKWQ7jQUKE4L6S8WVkyic0_5KqBj7tc_4gxQAAAAGw_lmDAA'''  # Add your string session here
)

BIN_API_URL = 'https://astroboyapi.com/api/bin.php?bin={}'

def filter_cards(text):
    regex = r'\d{16}.*\d{3}'
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

async def approved(Client, message):
    try:
        if re.search(r'(Approved!|Charged|authenticate_successful|𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱|APPROVED|New Cards Found By JennaScrapper|ꕥ Extrap [☭]|み RIMURU SCRAPE by|Approved) ✅', message.text):
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
                        f"⚜️Card ➔ <code>{card_info}</code>\n"
                        f"⚜️Status ➔ <b>Approved! ✅</b>\n"
                        "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -</b>\n"
                        f"⚜️Bin ➔ <b>{brand}, {card_type}, {level}</b>\n"
                        f"⚜️Bank ➔ <b>{bank}</b>\n"
                        f"⚜️Country ➔ <b>{country}, {country_flag}</b>\n"
                        "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -</b>\n"
                        "⚜️Creator ➔ <b>𝙅𝙚𝙩𝙞𝙭</b>"
                    )

                    await Client.send_message(chat_id='-1002222638488', text=formatted_message)

                    with open('reserved.txt', 'a', encoding='utf-8') as f:
                        f.write(card_info + '\n')
                else:
                    pass 
    except Exception as e:
        print(e)

@app.on_message(filters.text)
async def astro(Client, message):
    if message.text:
        await asyncio.create_task(approved(Client, message))

app.run()
