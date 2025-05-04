from pyrogram.errors.exceptions.bad_request_400 import StickerEmojiInvalid
import requests
import json
import subprocess
from pyrogram import Client, filters
from pyrogram.types.messages_and_media import message
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import FloodWait
from pyromod import listen
from pyrogram.types import Message
from p_bar import progress_bar
from subprocess import getstatusoutput
from aiohttp import ClientSession
import helper
from logger import logging
import time
import asyncio
from pyrogram.types import User, Message
from config import api_id, api_hash, bot_token, auth_users, sudo_users
import sys
import re
import os
from playwright.sync_api import sync_playwright

bot = Client(
    "bot",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token
)

@bot.on_message(filters.command(["stop"]))
async def cancel_command(bot: Client, m: Message):
    user_id = m.from_user.id if m.from_user is not None else None
    if user_id not in auth_users and user_id not in sudo_users:
        await m.reply(f"**You Are Not Subscribed To This Bot\nContact - @VictoryAnthem**", quote=True)
        return
    await m.reply_text("**STOPPED**🛑🛑", True)
    os.execl(sys.executable, sys.executable, *sys.argv)

@bot.on_message(filters.command(["start"]))
async def account_login(bot: Client, m: Message):
    user_id = m.from_user.id if m.from_user is not None else None
    if user_id not in auth_users and user_id not in sudo_users:
        await m.reply(f"**You Are Not Subscribed To This Bot\nContact - @VictoryAnthem**", quote=True)
        return

    editable = await m.reply_text(
        f"**Hey [{m.from_user.first_name}](tg://user?id={m.from_user.id})\nSend txt file**"
    )
    input_msg: Message = await bot.listen(editable.chat.id)
    if input_msg.document:
        x = await input_msg.download()
        await input_msg.delete(True)
        file_name, ext = os.path.splitext(os.path.basename(x))
        credit = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
        try:
            with open(x, "r") as f:
                content = f.read().split("\n")
            links = [line.split('://', 1) for line in content if line]
            os.remove(x)
        except:
            await m.reply_text("Invalid file input.🥲")
            os.remove(x)
            return
    else:
        content = input_msg.text.split("\n")
        links = [line.split('://', 1) for line in content if line]

    await editable.edit(
        f"Total links found are **{len(links)}**\n\nSend From where you want to download initial is **1**"
    )
    input0: Message = await bot.listen(editable.chat.id)
    raw_text = input0.text
    await input0.delete(True)

    await editable.edit("**Enter Batch Name or send d for grabbing from text filename.**")
    input1: Message = await bot.listen(editable.chat.id)
    raw_text0 = input1.text
    await input1.delete(True)
    b_name = file_name if raw_text0 == 'd' else raw_text0

    await editable.edit("**Enter resolution**")
    input2: Message = await bot.listen(editable.chat.id)
    raw_text2 = input2.text
    await input2.delete(True)
    res_map = {
        "144": "256x144",
        "240": "426x240",
        "360": "640x360",
        "480": "854x480",
        "720": "1280x720",
        "1080": "1920x1080"
    }
    res = res_map.get(raw_text2, "UN")

    await editable.edit("**Enter Your Name or send `de` for use default**")
    input3: Message = await bot.listen(editable.chat.id)
    raw_text3 = input3.text
    await input3.delete(True)
    CR = credit if raw_text3 == 'de' else raw_text3

    await editable.edit("**Enter Your PW Working Token\n\nOtherwise Send No**")
    input4: Message = await bot.listen(editable.chat.id)
    pw_token = input4.text
    await input4.delete(True)

    await editable.edit(
        "Now send the **Thumb url**\nEg : ```https://telegra.ph/file/0633f8b6a6f110d34f044.jpg```\n\nor Send No"
    )
    input6: Message = await bot.listen(editable.chat.id)
    await input6.delete(True)
    await editable.delete()

    thumb = input6.text
    if thumb.startswith("http://") or thumb.startswith("https://"):
        getstatusoutput(f"wget '{thumb}' -O 'thumb.jpg'")
        thumb = "thumb.jpg"
    else:
        thumb = None

    count = int(raw_text) if len(links) > 1 else 1

    try:
        for i in range(count - 1, len(links)):
            V = links[i][1].replace(
                "file/d/", "uc?export=download&id="
            ).replace(
                "www.youtube-nocookie.com/embed", "youtu.be"
            ).replace(
                "?modestbranding=1", ""
            ).replace(
                "/view?usp=sharing", ""
            )
            url = "https://" + V

            if "visionias" in url:
                async with ClientSession() as session:
                    async with session.get(
                        url,
                        headers={
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
                            'User-Agent': 'Mozilla/5.0'
                        }
                    ) as resp:
                        text = await resp.text()
                        url = re.search(r"(https://.*?playlist.m3u8.*?)\"", text).group(1)

            elif any(x in url for x in [
                'classplusapp', 'testbook.com', 'drm'
            ]):
                headers = {
                    'host': 'api.classplusapp.com',
                    'x-access-token': '...'
                }
                url = url.replace(
                    'https://tencdn.classplusapp.com/',
                    'https://media-cdn.classplusapp.com/tencent/'
                )
                res = requests.get(
                    "https://api.classplusapp.com/cams/uploader/video/jw-signed-url",
                    params={"url": url},
                    headers=headers
                ).json()
                url = res.get('drmUrls', {}).get('manifestUrl', res.get('url'))

            elif any(x in url for x in ["d1d34p8vz63oiq", "sec1.pw.live"]):
                url = f"https://anonymouspwplayer-b99f57957198.herokuapp.com/pw?url={url}?token={pw_token}"

            name1 = re.sub(r"[\t:/+#|@*.]|https?", "", links[i][0])
            name = f"{str(count).zfill(3)}) {name1[:60]}"

            ytf = (
                f"b[height<={raw_text2}][ext=mp4]/bv[height<={raw_text2}][ext=mp4]+ba[ext=m4a]/b[ext=mp4]"
                if "youtu" in url else
                f"b[height<={raw_text2}]/bv[height<={raw_text2}]+ba/b/bv+ba"
            )

            cmd = (
                f'yt-dlp -o "{name}.mp4" "{url}"'
                if "jw-prod" in url else
                f'yt-dlp -f "{ytf}" "{url}" -o "{name}.mp4"'
            )

            try:
                cc = f"**{str(count).zfill(3)}.** {name1}\n\n**Batch Name :** {b_name}\n\n**Downloaded by : {CR}**"
                if "drive" in url:
                    ka = await helper.download(url, name)
                    await bot.send_document(
                        chat_id=m.chat.id,
                        document=ka,
                        caption=cc
                    )
                    os.remove(ka)
                elif url.endswith(".pdf"):
                    os.system(cmd)
                    pdf_name = f"{name}.pdf"
                    await bot.send_document(
                        chat_id=m.chat.id,
                        document=pdf_name,
                        caption=cc
                    )
                    os.remove(pdf_name)
                else:
                    prog = await bot.send_message(
                        m.chat.id,
                        f"**Downloading:-**\n**Name:** {name}\n**Quality:** {raw_text2}\n" +
                        f"**Link:** {url}"
                    )
                    res_file = await helper.download_video(url, cmd, name)
                    await prog.delete(True)
                    await helper.send_vid(bot, m, cc, res_file, thumb, name)
                    os.remove(res_file)
                count += 1
            except FloodWait as e:
                await m.reply_text(str(e))
                time.sleep(e.x)
                count += 1
            except Exception as e:
                await m.reply_text(
                    f"**This #Failed File is not Counted**\n**Name** `{name}`\n**Link** `{url}`\n**Reason:** {e}"
                )
                count += 1
                continue
    except Exception as e:
        await bot.send_message(m.chat.id, str(e))
    await bot.send_message(m.chat.id, "🔰Done Boss🔰")

# /token command implementation\@@bot.on_message(filters.command(["token"]))
async def token_handler(bot: Client, m: Message):
    user_id = m.from_user.id if m.from_user else None
    if user_id not in auth_users and user_id not in sudo_users:
        return await m.reply("**Unauthorized**", quote=True)

    prompt = await m.reply_text(
        "📥 Send txt file or paste lines (title: URL with m3u8):"
    )
    inp: Message = await bot.listen(prompt.chat.id)
    lines = []
    if inp.document:
        fp = await inp.download()
        with open(fp, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f if l.strip()]
        os.remove(fp)
    else:
        lines = [l.strip() for l in inp.text.split("\n") if l.strip()]
    await prompt.delete(True)
    await inp.delete(True)

    entries = []
    for line in lines:
        if ":" in line and "http" in line:
            title, url = line.split(":", 1)
            entries.append((title.strip(), url.strip()))
        else:
            entries.append((None, line))

    count = 1
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for title, url in entries:
            note = await m.reply_text(f"🔍 Processing #{count}: {url}")
            vat_token = None
            def handle_request(request):
                nonlocal vat_token
                if "by-vat" in request.url and "vat=" in request.url:
                    vat_token = request.url.split("vat=")[-1].split("&")[0]
            page = browser.new_page()
            page.on("request", handle_request)
            try:
                page.goto(url, timeout=60000)
                for _ in range(30):
                    if vat_token:
                        break
                    time.sleep(1)
            except:
                await note.edit(f"❌ Failed to load: {url}")
                page.close()
                count += 1
                continue
            page.close()
            if not vat_token:
                await note.edit("❌ VAT not found.")
                count += 1
                continue

            vid_match = re.search(r"v=([a-fA-F0-9]+)", url)
            if not vid_match:
                await note.edit("❌ Video ID not found.")
                count += 1
                continue
            video_id = vid_match.group(1)

            player_url = f"https://web.vijethaiasacademy.com/api/vidrize/player-data/{video_id}?u=true&vat={vat_token}"
            try:
                r2 = requests.get(player_url, headers=HEADERS)
                data = r2.json()
                m3u8_url = data.get('signedVideo', {}).get('hlsUrl') or data.get('params', {}).get('hlsUrl')
                if not m3u8_url:
                    raise ValueError("m3u8 not found")
            except Exception as e:
                await note.edit(f"❌ Player fetch error: {e}")
                count += 1
                continue

            base_url = m3u8_url.split("/playlist.m3u8")[0]
            final_url = f"{base_url}/720p/video.m3u8"
            name = f"token_{str(count).zfill(3)}"
            cmd = f'yt-dlp -f best -o "{name}.mp4" "{final_url}"'

            try:
                await note.edit(f"🔄 Downloading #{count}")
                res_file = await helper.download_video(final_url, cmd, name)
                await note.delete(True)
                await helper.send_vid(bot, m, f"**Downloaded token stream #{count}**", res_file, None, name)
                os.remove(res_file)
            except Exception as e:
                await m.reply_text(f"❌ Download failed #{count}: {e}")
            count += 1
        browser.close()

    await m.reply_text("✅ Token downloads complete!")

bot.run()
