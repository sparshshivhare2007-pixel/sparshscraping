import asyncio
from pyrogram import Client, filters
import re
from pathlib import Path

API_ID = 26407665
API_HASH = "f10822a551f38b26ee1179e1a6515e01"
STRING_SESSION = "BQGS8vEAbqVDkE5huv23yFQQQcm5BJ5RYfeeeVBPad1wU4MImGPW5tGy0TeG1OKzGUOu7ikD9vePt8EI1F-JgjZdgxCkV1UGrk-54Kkp1yJ8-0ImJ7sdJgnyPm3FFBmCHlXvhmsdvnBI7waS_hbC_9PUyh27Q_6-uUY1570TZse2GtpHDB25NYTfQbg3_CjGvuiruS4f9E4NVSCOFRbtEU0v6TvKbzwKeeXcqI-Ep8dbYwG3aTIeJ5QUojDheGcHXrgibiO7Bn1jl_eheCyXtvQsMxFxJXaKaAGB7TwRsW1Sk0NRCY5ustO8_RzvT4oNZX0Xhwof912GW1xCc-LiaCaaGlsZ-gAAAAHjeyTmAA" # ADD YOUR STRING SESSION V2

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, session_string=STRING_SESSION)

def get_cards(text: str):
    text = text.replace('\n', ' ').replace('\r', '')
    card = re.findall(r"[0-9]+", text)
    if not card or len(card) < 3:
        return None

    if len(card) == 3:
        cc, mes_ano, cvv = card
        if len(mes_ano) == 3:
            mes, ano = mes_ano[:2], mes_ano[2:]
        else:
            mes, ano = mes_ano[:2], mes_ano[2:]
    elif len(card) > 3:
        cc, mes, ano, cvv = card[:4]
        if len(mes) != 2 or not ('01' <= mes <= '12'):
            mes, ano = ano, mes

    if not (cc.startswith(('3', '4', '5', '6')) and (len(cc) in [15, 16])):
        return None
    if len(mes) != 2 or not ('01' <= mes <= '12'):
        return None
    if len(ano) not in [2, 4] or (len(ano) == 2 and not ('21' <= ano <= '39')) or (len(ano) == 4 and not ('2021' <= ano <= '2039')):
        return None
    if cc.startswith('3') and len(cvv) != 4 or len(cvv) != 3:
        return None
    
    return cc, mes, ano, cvv

@app.on_message(filters.command('scr'))
async def cmd_scr(client, message):
    msg = message.text[len('/scr '):].strip()
    splitter = msg.split(' ')
    
    if not msg or len(splitter) < 2:
        resp = """
Wrong Format ❌

Usage:
For Public Group Scraping
/scr username 50

For Private Group Scraping
/scr https://t.me/+aGWRGz 50
        """
        await message.reply_text(resp)
        return

    try:
        limit = int(splitter[1])
    except ValueError:
        limit = 100

    delete = await message.reply_text("Scraping, Please Wait...", message.id)
    channel_link = splitter[0]
    
    async def scrape_channel(channel_id, limit, title):
        amt_cc = 0
        duplicate = 0
        async for msg in client.get_chat_history(channel_id, limit):
            all_history = msg.text or "INVALID CC NUMBER BC"
            all_cards = all_history.split('\n')
            cards = [get_cards(x) for x in all_cards if get_cards(x)]
            
            if not cards:
                continue
            
            file_name = f"{limit}x_CC_Scraped_By_Bot.txt"
            for item in cards:
                amt_cc += 1
                cc, mes, ano, cvv = item
                fullcc = f"{cc}|{mes}|{ano}|{cvv}"
                
                with open(file_name, 'a') as f:
                    cclist = open(file_name).read().splitlines()
                    if fullcc in cclist:
                        duplicate += 1
                    else:
                        f.write(f"{fullcc}\n")

        total_cc = amt_cc
        cc_found = total_cc - duplicate
        await app.delete_messages(message.chat.id, delete.id)
        caption = f"""
CC Scraped ✅

Source: {title}
Targeted Amount: {limit}
CC Found: {cc_found}
Duplicate Removed: {duplicate}
Scraped By: <a href="tg://user?id={message.from_user.id}"> {message.from_user.first_name}</a> ♻️
"""
        document = file_name
        scr_done = await app.send_document(
            message.chat.id,
            document=document,
            caption=caption,
            reply_to_message_id=message.id
        )

        if scr_done:
            Path(file_name).unlink(missing_ok=True)

    try:
        if "https" in channel_link:
            join = await client.join_chat(channel_link)
            await scrape_channel(join.id, limit, join.title)
        else:
            chat_info = await client.get_chat(channel_link)
            await scrape_channel(chat_info.id, limit, chat_info.title)
    except Exception as e:
        error_message = str(e)
        if '[400 USER_ALREADY_PARTICIPANT]' in error_message:
            chat_info = await client.get_chat(channel_link)
            await scrape_channel(chat_info.id, limit, chat_info.title)
        elif '[400 USERNAME_INVALID]' in error_message:
            resp = """
Wrong Format ❌

Usage:
For Public Group Scraping
/scr username 50

For Private Group Scraping
/scr https://t.me/+aGWRGz 50
        """
            await message.reply_text(resp)
            await delete.delete()
        elif '[400 INVITE_HASH_EXPIRED]' in error_message:
            await message.reply_text("The invite link is expired. Please provide a valid link.", message.id)
            await delete.delete()
        else:
            await message.reply_text(f"An error occurred: {error_message}", message.id)
            await delete.delete()

app.run()
          
