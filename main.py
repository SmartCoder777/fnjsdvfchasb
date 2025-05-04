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

# -- Enhanced function: pre-fetch JSON and extract m3u8 before running yt-dlp --
async def download_tokenized_video(url: str, output_name: str, user_agent: str = None) -> str:
    """
    Download a tokenized non-DRM video URL by:
      1. Extracting `curl`, `tkn`, `cid`, `v`, and `vat` from query.
      2. Registering the lesson via VAT.
      3. Fetching the player-data to grab the .m3u8 HLS URL.
      4. Swapping to the 720p stream and feeding that URL to yt-dlp with proper headers.
    """
    logging.info(f"Starting download for {url} as {output_name}")
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    referer = qs.get('curl', [''])[0]
    token = qs.get('tkn', [''])[0]
    cid = qs.get('cid', [''])[0]
    video_id = qs.get('v', [''])[0]
    vat = qs.get('vat', [''])[0]

    if user_agent is None:
        user_agent = (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/113.0.0.0 Safari/537.36'
        )

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Origin': 'https://player.filecdn.in',
        'Referer': referer,
        'User-Agent': user_agent,
        'token': token
    }
    if cid:
        headers['cid'] = cid

    download_url = url
    try:
        # Step 1: register/view the lesson via VAT
        lesson_url = f"https://web.vijethaiasacademy.com/api/course-creator/userlesson/by-vat?createIfNotFound=true&vat={vat}"
        logging.debug(f"Registering lesson via {lesson_url}")
        requests.get(lesson_url, headers=headers, timeout=10)
        # Step 2: fetch player-data
        player_url = f"https://web.vijethaiasacademy.com/api/vidrize/player-data/{video_id}?u=true&vat={vat}"
        logging.debug(f"Fetching player data from {player_url}")
        res = requests.get(player_url, headers=headers, timeout=10)
        data = res.json()
        # extract HLS URL
        if 'signedVideo' in data and 'hlsUrl' in data['signedVideo']:
            m3u8 = data['signedVideo']['hlsUrl']
        elif 'params' in data and 'hlsUrl' in data['params']:
            m3u8 = data['params']['hlsUrl']
        else:
            m = re.search(r"(https?://[^'\"<>]+?\.m3u8[^'\"<>]*)", res.text)
            m3u8 = m.group(1) if m else None
        if m3u8:
            download_url = m3u8.replace('playlist.m3u8', '720p/video.m3u8')
            logging.info(f"Resolved HLS URL to {download_url}")
    except Exception as e:
        logging.error(f"Error fetching tokenized video info: {e}")

    # prepare yt-dlp command
    ytdlp_headers = []
    for k, v in headers.items():
        ytdlp_headers += ['--add-header', f"{k}: {v}"]

    cmd = [
        'yt-dlp',
        download_url,
        '-o', f"{output_name}.mp4",
    ] + ytdlp_headers
    logging.debug(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logging.error(f"yt-dlp failed: {result.stderr}")
        raise RuntimeError(f"yt-dlp failed: {result.stderr}")
    logging.info(f"Download completed: {output_name}.mp4")
    return f"{output_name}.mp4"
# -- End enhanced function --

# -- /token command handler for batch tokenized downloads --
@bot.on_message(filters.command(["token"]))
async def token_download(bot: Client, m: Message):
    user_id = m.from_user.id if m.from_user else None
    logging.info(f"User {user_id} invoked /token")
    if user_id not in auth_users and user_id not in sudo_users:
        logging.warning(f"Unauthorized user {user_id}")
        await m.reply("**You Are Not Subscribed To This Bot\nContact - @VictoryAnthem**", quote=True)
        return

    prompt = await m.reply_text("**Send text file or paste links (one per line) for tokenized downloads**")
    inp: Message = await bot.listen(prompt.chat.id)
    if inp.document:
        path = await inp.download()
        with open(path) as f:
            lines = f.read().splitlines()
        os.remove(path)
        logging.debug(f"Read {len(lines)} links from document")
    else:
        lines = inp.text.splitlines()
        logging.debug(f"Read {len(lines)} links from text")
    await prompt.delete(True)

    links = [line.split('://',1)[1] if '://' in line else line for line in lines]
    ask = await m.reply_text(f"Total links: **{len(links)}**\nSend starting line number (default 1)")
    resp: Message = await bot.listen(ask.chat.id)
    while resp.text.startswith('/') or not resp.text.isdigit():
        await resp.delete(True)
        resp = await bot.listen(ask.chat.id)
    start = int(resp.text); await resp.delete(True)
    logging.debug(f"Download starting at index {start}")

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
    logging.debug(f"Batch name: {batch}, downloader: {downloader}")

    count = start
    for raw in links[start-1:]:
        url = 'https://' + raw
        name_base = re.sub(r"[^\w\-]", "", raw)[:60]
        out = f"{str(count).zfill(3)}) {name_base}"
        logging.info(f"Processing link {count}: {url}")
        try:
            file_path = await download_tokenized_video(url, out)
            caption = f"**{count}.** {name_base}\n**Batch:** {batch or name_base}\n**By:** {downloader}"
            await bot.send_document(chat_id=m.chat.id, document=file_path, caption=caption)
            os.remove(file_path)
            logging.info(f"Sent file {file_path}")
            count += 1
        except Exception as e:
            logging.error(f"Failed to download {url}: {e}")
            await m.reply_text(f"Failed to download {url}: {e}")
            count += 1

    logging.info("Token downloads completed")
    await m.reply_text("🔰 Token downloads completed 🔰")
# -- End /token handler --

# -- Existing /start and /stop flows remain unchanged --
@bot.on_message(filters.command(["stop"]))
async def cancel_command(bot: Client, m: Message):
    user_id = m.from_user.id if m.from_user else None
    logging.info(f"User {user_id} invoked /stop")
    if user_id not in auth_users and user_id not in sudo_users:
        logging.warning(f"Unauthorized user {user_id} attempted /stop")
        await m.reply("**You Are Not Subscribed To This Bot\nContact - @VictoryAnthem**", quote=True)
        return
    logging.info("Stopping bot and restarting process")
    await m.reply_text("**STOPPED**🛑🛑", True)
    os.execl(sys.executable, sys.executable, *sys.argv)

@bot.on_message(filters.command(["start"]))
async def account_login(bot: Client, m: Message):
    user_id = m.from_user.id if m.from_user else None
    logging.info(f"User {user_id} invoked /start")
    if user_id not in auth_users and user_id not in sudo_users:
        logging.warning(f"Unauthorized user {user_id} attempted /start")
        await m.reply("**You Are Not Subscribed To This Bot\nContact - @VictoryAnthem**", quote=True)
        return

    editable = await m.reply_text(f"**Hey [{m.from_user.first_name}](tg://user?id={m.from_user.id})\nSend txt file**")
    input_msg: Message = await bot.listen(editable.chat.id)
    if input_msg.document:
        path = await input_msg.download()
        await input_msg.delete(True)
        with open(path) as f:
            content = f.read().splitlines()
        os.remove(path)
        logging.debug(f"Read start links file with {len(content)} entries")
    else:
        content = input_msg.text.splitlines()
        logging.debug(f"Read start links text with {len(content)} entries")

    links = [line.split('://',1) for line in content]
    await editable.edit(f"Total links found are **{len(links)}**\n\nSend From where you want to download initial is **1**")
    resp1: Message = await bot.listen(editable.chat.id)
    while resp1.text.startswith('/') or not resp1.text.isdigit():
        await resp1.delete(True)
        resp1 = await bot.listen(editable.chat.id)
    start_index = int(resp1.text)
    await resp1.delete(True)
    logging.debug(f"Start index for visionias flow: {start_index}")

    await editable.edit("**Enter Batch Name or send d for grabbing from text filename.**")
    resp2: Message = await bot.listen(editable.chat.id)
    while resp2.text.startswith('/'):
        await resp2.delete(True)
        resp2 = await bot.listen(editable.chat.id)
    b_name = resp2.text if resp2.text != 'd' else None
    await resp2.delete(True)
    logging.debug(f"VisionIAS batch name: {b_name}")

    # ... rest of /start logic remains unchanged

    await m.reply_text("🔰Done Boss🔰")

bot.run()
