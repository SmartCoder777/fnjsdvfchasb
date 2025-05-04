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
from pyrogram import Client, filters  
from p_bar import progress_bar  
from subprocess import getstatusoutput  
from aiohttp import ClientSession  
import helper  
from logger import logging  
import time  
import asyncio  
from pyrogram.types import User, Message  
from config import api_id, api_hash, bot_token, auth_users, sudo_users  
import os  
import re  

bot = Client(
    "bot",
    api_id=29754529,
    api_hash="dd54732e78650479ac4fb0e173fe4759",
    bot_token="7719885018:AAEHHG6-cby4xjYb2t71_vb8Rt5zInTKvNM"
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
          
    editable = await m.reply_text(f"**Hey [{m.from_user.first_name}](tg://user?id={m.from_user.id})\nSend txt file**")  
    input: Message = await bot.listen(editable.chat.id)  
    if input.document:  
        x = await input.download()  
        await input.delete(True)  
        file_name, ext = os.path.splitext(os.path.basename(x))  
        credit = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"  
        path = f"./downloads/{m.chat.id}"  

        try:  
            with open(x, "r") as f:  
                content = f.read()  
            content = content.split("\n")  
            links = []  
            for i in content:  
                links.append(i.split("://", 1))  
            os.remove(x)  
              
        except:  
            await m.reply_text("Invalid file input.🥲")  
            os.remove(x)  
            return  
    else:  
        content = input.text  
        content = content.split("\n")  
        links = []  
        for i in content:  
            links.append(i.split("://", 1))  
     
    await editable.edit(f"Total links found are **{len(links)}**\n\nSend From where you want to download initial is **1**")  
    input0: Message = await bot.listen(editable.chat.id)  
    raw_text = input0.text  
    await input0.delete(True)  

    await editable.edit("**Enter Batch Name or send d for grabing from text filename.**")  
    input1: Message = await bot.listen(editable.chat.id)  
    raw_text0 = input1.text  
    await input1.delete(True)  
    if raw_text0 == 'd':  
        b_name = file_name  
    else:  
        b_name = raw_text0  

    await editable.edit("**Enter resolution**")  
    input2: Message = await bot.listen(editable.chat.id)  
    raw_text2 = input2.text  
    await input2.delete(True)  
    try:  
        if raw_text2 == "144":  
            res = "256x144"  
        elif raw_text2 == "240":  
            res = "426x240"  
        elif raw_text2 == "360":  
            res = "640x360"  
        elif raw_text2 == "480":  
            res = "854x480"  
        elif raw_text2 == "720":  
            res = "1280x720"  
        elif raw_text2 == "1080":  
            res = "1920x1080"   
        else:   
            res = "UN"  
    except Exception:  
            res = "UN"  
      
    await editable.edit("**Enter Your Name or send `de` for use default**")  
    input3: Message = await bot.listen(editable.chat.id)  
    raw_text3 = input3.text  
    await input3.delete(True)  
    if raw_text3 == 'de':  
        CR = credit  
    else:  
        CR = raw_text3  

    await editable.edit("**Enter Your PW Woking Token\n\nOtherwise Send No**")  
    input4: Message = await bot.listen(editable.chat.id)  
    pw_token = input4.text  
    await input4.delete(True)  

    await editable.edit("Now send the **Thumb url**\nEg : ```https://telegra.ph/file/0633f8b6a6f110d34f044.jpg```\n\nor Send No`")  
    input6 = message = await bot.listen(editable.chat.id)  
    raw_text6 = input6.text  
    await input6.delete(True)  
    await editable.delete()  

    thumb = input6.text  
    if thumb.startswith("http://") or thumb.startswith("https://"):  
        getstatusoutput(f"wget '{thumb}' -O 'thumb.jpg'")  
        thumb = "thumb.jpg"  
    else:  
        thumb == "No"  

    if len(links) == 1:  
        count = 1  
    else:  
        count = int(raw_text)  

    try:  
        for i in range(count - 1, len(links)):  

            V = links[i][1].replace("file/d/","uc?export=download&id=").replace("www.youtube-nocookie.com/embed", "youtu.be").replace("?modestbranding=1", "").replace("/view?usp=sharing","")  
            url = "https://" + V  

            if "visionias" in url:  
                async with ClientSession() as session:  
                    async with session.get(url, headers={...}) as resp:  
                        text = await resp.text()  
                        url = re.search(r"(https://.*?playlist.m3u8.*?)\"", text).group(1)  

            elif 'classplusapp' in url or ... :  
                headers = {...}  
                url = url.replace(...)  
                params = {"url": f"{url}"}  
                res = requests.get(..., params=params, headers=headers).json()  
                if ...:  
                    url = res['drmUrls']['manifestUrl']  
                else:  
                    url = res["url"]  

            elif "d1d34p8vz63oiq" in url or "sec1.pw.live" in url:  
                url = f"https://anonymouspwplayer-.../?url={url}?token={pw_token}"  
            else:  
                url = url  
                
            name1 = links[i][0].replace(...).strip()  
            name = f'{str(count).zfill(3)}) {name1[:60]}'  

            if "youtu" in url:  
                ytf = f"b[height<={raw_text2}][ext=mp4]/bv...+ba[ext=m4a]/b[ext=mp4]"  
            else:  
                ytf = f"b[height<={raw_text2}]/bv...+ba/b/bv+ba"  

            if "jw-prod" in url:  
                cmd = f'yt-dlp -o "{name}.mp4" "{url}"'  
            else:  
                cmd = f'yt-dlp -f "{ytf}" "{url}" -o "{name}.mp4"'  

            try:                                
                cc = f'** {str(count).zfill(3)}.** {name1}\n\n**Batch Name :** {b_name}\n\n**Downloaded by : {CR}**'  
                cc1 = f'** {str(count).zfill(3)}.** {name1}\n\n**Batch Name :**{b_name}\n\n**Downloaded by : {CR}**'  
                if "drive" in url:  
                    ...  
                elif ".pdf" in url:  
                    ...  
                else:  
                    prog = await m.reply_text(...)  
                    res_file = await helper.download_video(url, cmd, name)  
                    await prog.delete(True)  
                    await helper.send_vid(bot, m, cc, filename, thumb, name)  
                    count += 1  

            except Exception as e:  
                await m.reply_text(f"...{e}")  
                count += 1  
                continue  

    except Exception as e:  
        await m.reply_text(e)  
    await m.reply_text("🔰Done Boss🔰")  

@bot.on_message(filters.command(["token"]))  
async def single_token(bot: Client, m: Message):  
    ...  # unchanged  

def run_ffmpeg_decrypt(m3u8_url: str, key_hex: str, out_mp4: str):
    # create a unique temp dir
    tmp = f"/tmp/{uuid.uuid4().hex}"
    os.makedirs(tmp, exist_ok=True)

    # 1) download the playlist
    playlist_path = os.path.join(tmp, "playlist.m3u8")
    r = requests.get(m3u8_url, timeout=15)
    r.raise_for_status()
    with open(playlist_path, "w", encoding="utf-8") as f:
        f.write(r.text)

    # 2) write raw key file
    key_bin = bytes.fromhex(key_hex)
    key_path = os.path.join(tmp, "file.key")
    with open(key_path, "wb") as f:
        f.write(key_bin)

    # 3) write key info file for ffmpeg
    #    <URI-on-playlist or dummy>  
    #    <local-key-path>  
    #    <IV hex or blank>
    ki_path = os.path.join(tmp, "keyinfo.txt")
    with open(ki_path, "w") as f:
        f.write(f"{key_path}\n{key_path}\n")

    # 4) run ffmpeg with HLS keyfile
    cmd = [
        "ffmpeg",
        "-allowed_extensions", "ALL",
        "-protocol_whitelist", "file,http,https,tcp,tls",
        "-hls_key_info_file", ki_path,
        "-i", playlist_path,
        "-c", "copy",
        out_mp4
    ]
    subprocess.run(cmd, check=True)

    # 5) cleanup temp
    for fn in os.listdir(tmp):
        os.remove(os.path.join(tmp, fn))
    os.rmdir(tmp)


@bot.on_message(filters.command(["graphy"]))
async def graphy_handler(bot: Client, m: Message):
    uid = m.from_user.id
    if uid not in auth_users and uid not in sudo_users:
        return await m.reply("**Not subscribed. Contact @VictoryAnthem**", quote=True)

    # 1) get .txt
    msg = await m.reply("📄 Send .txt of lines:\n  (Title) (video):<m3u8>HLS_KEY=<hex>")
    inp = await bot.listen(m.chat.id)
    if not inp.document or not inp.document.file_name.endswith(".txt"):
        return await msg.edit("❌ Invalid .txt")
    path = await inp.download()
    await msg.edit("✅ Received.")

    # 2) get start line
    ask = await m.reply("▶️ Start from which line? (1-based)")
    num = await bot.listen(m.chat.id)
    try:
        start = max(1, int(num.text))
    except:
        start = 1
    await ask.delete()

    # 3) read lines & process
    with open(path, "r", encoding="utf-8") as f:
        lines = [L.strip() for L in f if ":" in L]
    os.remove(path)

    total = len(lines) - (start - 1)
    await m.reply(f"🔢 Downloading {total} items from line {start}…")

    for idx, line in enumerate(lines[start-1:], start=start):
        try:
            title_part, rest = line.split(":",1)
            title = title_part.strip("() ").strip()
            if "HLS_KEY=" not in rest:
                raise ValueError("no HLS_KEY")
            url_str, key_hex = rest.split("HLS_KEY=",1)
            url = url_str.strip()
            key = key_hex.strip()

            safe = re.sub(r'[<>:"/\\|?*]', "_", f"{idx:03d}) {title}")
            os.makedirs("downloads", exist_ok=True)
            outp = os.path.abspath(f"downloads/{safe}.mp4")

            if os.path.exists(outp):
                await m.reply(f"⏭️ {safe} exists, skipping")
                continue

            await m.reply(f"▶️ {safe}")
            # run in executor
            await asyncio.get_event_loop().run_in_executor(
                None, run_ffmpeg_decrypt, url, key, outp
            )

            # send & cleanup
            await bot.send_document(m.chat.id, outp, caption=safe)
            os.remove(outp)

        except Exception as e:
            await m.reply(f"❌ Line {idx} failed: {e}")

    await m.reply("✅ All done!")

bot.run()  
