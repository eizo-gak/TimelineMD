import discord
import os
import re
from datetime import datetime, timedelta
from discord.ext import commands

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def zenkaku_to_hankaku(text):
    return text.translate(str.maketrans("０１２３４５６７８９", "0123456789"))

def get_current_time_jst():
    now_utc = datetime.utcnow()
    jst = now_utc + timedelta(hours=9)
    return jst.strftime("%H:%M")

def convert_message(content):
    match = re.match(r"^([０-９]{4})(.+?)。。(.+)", content)
    match_no_time = re.match(r"^。。(.+?)。。(.+)", content)

    if match:
        full_width_time, title, body = match.groups()
        half_width_time = zenkaku_to_hankaku(full_width_time)
        hour, minute = int(half_width_time[:2]), int(half_width_time[2:])
        formatted_time = f"{hour:02d}:{minute:02d}" if hour < 26 and minute < 60 else get_current_time_jst()
    elif match_no_time:
        title, body = match_no_time.groups()
        formatted_time = get_current_time_jst()
    else:
        return None

    url_pattern = r"(https?://)?(www\.)?[\w\-]+\.[a-z]{2,}(/?[\w\-./?%&=]*)?"
    url_match = re.search(url_pattern, body)

    if url_match:
        url = url_match.group(0)
        body = body.replace(url, '').strip()
        return f"↓\n## ・{formatted_time} {title}\n```\n{body}\n```{url}"
    else:
        return f"↓\n## ・{formatted_time} {title}\n```\n{body}\n```"

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message):
        await message.channel.send("こんにちは！何かお手伝いしますか？")

    converted_text = convert_message(message.content)

    if converted_text:
        files = [await attachment.to_file() for attachment in message.attachments]
        await message.channel.send(converted_text, files=files)
        await message.delete()

    await bot.process_commands(message)

bot.run(TOKEN)
