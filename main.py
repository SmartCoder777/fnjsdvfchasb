from urllib.parse import urlparse, parse_qs
import subprocess
import requests
import json
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.errors import FloodWait
from pyromod import listen
from aiohttp import ClientSession
import helper
from logger import logging
import time
import asyncio
import sys
import re
import os
from config import api_id, api_hash, bot_token, auth_users, sudo_users

bot = Client(
    "bot",
    api_id=29754529,
    api_hash="dd54732e78650479ac4fb0e173fe4759",
    bot_token="7719885018:AAEHHG6-cby4xjYb2t71_vb8Rt5zInTKvNM"
)

# -- Updated function: no format flag for tokenized links --
async def download_tokenized_video(url: str, output_name: str, user_agent: str = None) -> str:
    """
    Download a tokenized non-DRM video URL using yt-dlp by extracting:
      - `curl` as Referer header
      - `tkn` as Authorization Bearer token
      - `cid` as custom header
    Does not pass any -f flag so yt-dlp picks best available automatically.
    """
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    referer = qs.get('curl', [''])[0]
    token = qs.get('tkn', [''])[0]
    cid = qs.get('cid', [''])[0]

    if user_agent is None:
        user_agent = (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/113.0.0.0 Safari/537.36'
        )

    headers = [
        '--add-header', f"Referer: {referer}",
        '--add-header', f"User-Agent: {user_agent}",
    ]
    if token:
        headers += ['--add-header', f"Authorization: Bearer {token}"]
    if cid:
        headers += ['--add-header', f"cid: {cid}"]

    # no '-f' provided
    cmd = [
        'yt-dlp',
        url,
        '-o', f"{output_name}.mp4",
    ] + headers

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"yt-dlp failed: {result.stderr}")
    return f"{output_name}.mp4"
# -- End update --

# -- New /token command handler: simplified flow for tokenized links --
@bot.on_message(filters.command(["token"]))
async def token_download(bot: Client, m: Message):
    user_id = m.from_user.id if m.from_user else None
    if user_id not in auth_users and user_id not in sudo_users:
        await m.reply("**You Are Not Subscribed To This Bot\nContact - @VictoryAnthem**", quote=True)
        return

    prompt = await m.reply_text("**Send text file or paste links (one per line) for tokenized downloads**")
    inp: Message = await bot.listen(prompt.chat.id)
    if inp.document:
        path = await inp.download()
        with open(path) as f:
            lines = f.read().splitlines()
        os.remove(path)
    else:
        lines = inp.text.splitlines()
    await prompt.delete(True)

    links = [line.split('://',1)[1] if '://' in line else line for line in lines]
    ask = await m.reply_text(f"Total links: **{len(links)}**\nSend starting line number (default 1)")
    resp: Message = await bot.listen(ask.chat.id)
    while resp.text.startswith('/') or not resp.text.isdigit():
        await resp.delete(True)
        resp = await bot.listen(ask.chat.id)
    start = int(resp.text); await resp.delete(True)

    ask2 = await m.reply_text("**Enter Batch Name or send `d` for default**")
    resp2: Message = await bot.listen(ask2.chat.id)
    while resp2.text.startswith('/'):
        await resp2.delete(True)
        resp2 = await bot.listen(ask2.chat.id)
    batch = None if resp2.text == 'd' else resp2.text
    await resp2.delete(True)

    ask3 = await m.reply_text("**Enter 'de' to use your name or type custom 'Downloaded by'**")
    resp3: Message = await bot.listen(ask3.chat.id)
    while resp3.text.startswith('/'):
        await resp3.delete(True)
        resp3 = await bot.listen(ask3.chat.id)
    downloader = resp3.text if resp3.text != 'de' else f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
    await resp3.delete(True)

    count = start
    for raw in links[start-1:]:
        url = 'https://' + raw
        name_base = re.sub(r"[^\w\-]", "", raw)[:60]
        out = f"{str(count).zfill(3)}) {name_base}"
        try:
            file_path = await download_tokenized_video(url, out)
            caption = f"**{count}.** {name_base}\n**Batch:** {batch or name_base}\n**By:** {downloader}"
            await bot.send_document(chat_id=m.chat.id, document=file_path, caption=caption)
            os.remove(file_path)
            count += 1
        except Exception as e:
            await m.reply_text(f"Failed to download tokenized link {url}: {e}")
            count += 1
    await m.reply_text("🔰 Token downloads completed 🔰")
# -- End /token handler --

async def cancel_command(bot: Client, m: Message):
    user_id = m.from_user.id if m.from_user else None
    if user_id not in auth_users and user_id not in sudo_users:
        await m.reply("**You Are Not Subscribed To This Bot\nContact - @VictoryAnthem**", quote=True)
        return
    await m.reply_text("**STOPPED**🛑🛑", True)
    os.execl(sys.executable, sys.executable, *sys.argv)

@bot.on_message(filters.command(["start"]))
async def account_login(bot: Client, m: Message):
    user_id = m.from_user.id if m.from_user else None
    if user_id not in auth_users and user_id not in sudo_users:
        await m.reply("**You Are Not Subscribed To This Bot\nContact - @VictoryAnthem**", quote=True)
        return

    editable = await m.reply_text(f"**Hey [{m.from_user.first_name}](tg://user?id={m.from_user.id})\nSend txt file**")
    input_msg: Message = await bot.listen(editable.chat.id)
    # parse links from txt file or plain text
    if input_msg.document:
        path = await input_msg.download()
        await input_msg.delete(True)
        with open(path) as f:
            content = f.read().splitlines()
        os.remove(path)
    else:
        content = input_msg.text.splitlines()

    links = [line.split('://',1) for line in content]
    await editable.edit(f"Total links found are **{len(links)}**\n\nSend From where you want to download initial is **1**")
    # listen for start index, ignore any commands
    resp1: Message = await bot.listen(editable.chat.id)
    while resp1.text.startswith('/') or not resp1.text.isdigit():
        await resp1.delete(True)
        resp1 = await bot.listen(editable.chat.id)
    start_index = int(resp1.text)
    await resp1.delete(True)

    await editable.edit("**Enter Batch Name or send d for grabbing from text filename.**")
    resp2: Message = await bot.listen(editable.chat.id)
    while resp2.text.startswith('/'):
        await resp2.delete(True)
        resp2 = await bot.listen(editable.chat.id)
    b_name = resp2.text if resp2.text != 'd' else None
    await resp2.delete(True)

    await editable.edit("**Enter resolution**")
    resp3: Message = await bot.listen(editable.chat.id)
    while resp3.text.startswith('/'):
        await resp3.delete(True)
        resp3 = await bot.listen(editable.chat.id)
    req_res = resp3.text; await resp3.delete(True)
    res_map = {"144":"256x144","240":"426x240","360":"640x360","480":"854x480","720":"1280x720","1080":"1920x1080"}
    res = res_map.get(req_res, "UN")

    await editable.edit("**Enter Your Name or send `de` for default**")
    resp4: Message = await bot.listen(editable.chat.id)
    while resp4.text.startswith('/'):
        await resp4.delete(True)
        resp4 = await bot.listen(editable.chat.id)
    credit = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
    CR = credit if resp4.text == 'de' else resp4.text
    await resp4.delete(True)

    await editable.edit("**Enter PW Token or send No**")
    resp5: Message = await bot.listen(editable.chat.id)
    while resp5.text.startswith('/'):
        await resp5.delete(True)
        resp5 = await bot.listen(editable.chat.id)
    pw_token = resp5.text; await resp5.delete(True)

    await editable.edit("Send Thumb URL or No")
    resp6: Message = await bot.listen(editable.chat.id)
    while resp6.text.startswith('/'):
        await resp6.delete(True)
        resp6 = await bot.listen(editable.chat.id)
    thumb = resp6.text
    await resp6.delete(True); await editable.delete()
    if thumb.startswith("http"): os.system(f"wget '{thumb}' -O thumb.jpg"); thumb = "thumb.jpg"

    count = start_index
    for idx in range(start_index-1, len(links)):
        raw = links[idx][1]
        url = 'https://' + raw
        name_base = re.sub(r"[^\w\-]", "", links[idx][0])[:60]
        out_name = f"{str(count).zfill(3)}) {name_base}"

        # tokenized vidrize links
        if 'player.filecdn.in/vidrize' in url:
            try:
                file_path = await download_tokenized_video(url, out_name)
                await bot.send_document(chat_id=m.chat.id, document=file_path,
                                        caption=f"**{count}.** {name_base}\n**Batch:** {b_name or name_base}\n**By:** {CR}")
                os.remove(file_path)
                count += 1
                continue
            except Exception as e:
                await m.reply_text(f"Failed to download tokenized link {url}: {e}")
                count += 1
                continue

        # existing handlers
        if "visionias" in url:
            async with ClientSession() as session:
                async with session.get(url, headers={
                    'Referer':'http://www.visionias.in/', 'User-Agent': 'Mozilla/5.0'
                }) as resp:
                    text = await resp.text()
                    url = re.search(r"(https://.*?playlist.m3u8.*?)\"", text).group(1)

        # yt-dlp download fallback
        fmt = f"b[height<={req_res}]+ba" if "youtu" not in url else f"b[height<={req_res}][ext=mp4]+ba[ext=m4a]"
        cmd = f'yt-dlp -f "{fmt}" "{url}" -o "{out_name}.mp4"'
        try:
            prog = await m.reply_text(f"Downloading {out_name}")
            res_file = await helper.download_video(url, cmd, out_name)
            await prog.delete(True)
            await helper.send_vid(bot, m, f"**{count}.** {name_base}\n**Batch:** {b_name or name_base}\n**By:** {CR}", res_file, thumb, out_name)
            count += 1
        except FloodWait as e:
            await m.reply_text(str(e)); time.sleep(e.x); continue
        except Exception as e:
            await m.reply_text(f"Failed {out_name}: {e}")
            count += 1
            continue

    await m.reply_text("🔰Done Boss🔰")

bot.run()
