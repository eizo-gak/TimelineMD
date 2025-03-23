import discord
import os
import re
from datetime import datetime, timedelta
from discord.ext import commands

# セッション時間を生かす（UptimeRobotで定期Ping）
from flask import Flask
from threading import Thread

# セッション時間を生かす2
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    thread = Thread(target=run)
    thread.start()



# 環境変数からトークンを取得
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Botの設定
intents = discord.Intents.default()
intents.message_content = True  # メッセージ内容の取得を許可

bot = commands.Bot(command_prefix="!", intents=intents)


# 全角数字を半角に変換する関数
def zenkaku_to_hankaku(text):
    return text.translate(str.maketrans("０１２３４５６７８９", "0123456789"))


# 現在時刻（JST）をHH:MM形式で取得する関数
def get_current_time_jst():
    now_utc = datetime.utcnow()
    jst = now_utc + timedelta(hours=9)  # JSTはUTC+9時間
    return jst.strftime("%H:%M")


# メッセージを変換する関数
def convert_message(content):
    match = re.match(r"^([０-９]{4})(.+?)。。(.+)", content)  # 時刻指定パターン
    match_no_time = re.match(r"^。。(.+?)。。(.+)", content)  # JST時刻使用パターン

    if match:
        full_width_time, title, body = match.groups()
        half_width_time = zenkaku_to_hankaku(full_width_time)
        hour, minute = int(half_width_time[:2]), int(half_width_time[2:])
        formatted_time = f"{hour:02d}:{minute:02d}" if hour < 26 and minute < 60 else get_current_time_jst(
        )
    elif match_no_time:
        title, body = match_no_time.groups()
        formatted_time = get_current_time_jst()
    else:
        return None

    # URLが含まれているかどうかをチェック
    url_pattern = r'(https?://)?(www\.)?[\w\-]+\.[a-z]{2,}(/?[\w\-./?%&=]*)?'
    url_match = re.search(url_pattern, body)

    if url_match:
        url = url_match.group(0)
        body = body.replace(url, '').strip()
        return f"↓\n## ・{formatted_time} {title}\n```\n{body}\n```{url}"
    else:
        return f"↓\n## ・{formatted_time} {title}\n```\n{body}\n```"


# メッセージが送信されたとき
@bot.event
async def on_message(message):
    if message.author == bot.user:  # 自分のメッセージは無視
        return

    converted_text = convert_message(message.content)

    if converted_text:
        files = [
            await attachment.to_file() for attachment in message.attachments
        ]  # 添付画像も取得
        await message.channel.send(converted_text, files=files)
        await message.delete()  # 元のメッセージを削除

    await bot.process_commands(message)  # コマンド処理を続行

# セッション生かす実行コマンド
keep_alive()

# Botを起動
bot.run(TOKEN)
