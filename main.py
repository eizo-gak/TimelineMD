import discord
import os
import re
from datetime import datetime, timedelta
from discord.ext import commands

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
    match = re.match(r"^([０-９]{4})(.+?)。。(.+)", content)
    if match:
        full_width_time = match.group(1)  # 時刻（例: ２３５５）
        title = match.group(2).strip()  # h2タイトル
        body = match.group(3).strip()  # 記事本文

        # 時刻を半角に変換
        half_width_time = zenkaku_to_hankaku(
            full_width_time)  # 例: "２３５５" → "2355"

        # 時刻フォーマットを修正（2355 → 23:55）
        hour = int(half_width_time[:2])
        minute = int(half_width_time[2:])

        # 時刻が不正な場合（例: 分が60以上）
        if hour >= 24 or minute >= 60:
            formatted_time = get_current_time_jst()  # 不正な時刻は現在時刻を使用
        else:
            # 26時台も許容（例: 26:30）
            if hour >= 26:
                formatted_time = f"{hour}:{minute:02d}"  # 26:30 の形式
            else:
                formatted_time = f"{hour:02d}:{minute:02d}"  # 通常の時刻

        # URLが含まれているかどうかをチェック（短縮URLも可）
        url_pattern = r'(https?://)?(www\.)?[\w\-]+\.[a-z]{2,}(/[\w\-./?%&=]*)?'
        url_match = re.search(url_pattern, body)

        # URLがある場合、そのURLをメッセージに追加
        if url_match:
            url = url_match.group(0)
            body = body.replace(url, '')  # 本文からURLを削除

            # 変換後のメッセージにURLを追加
            return f"↓\n## ・{formatted_time} {title}\n```\n{body}\n```{url}"
        else:
            return f"↓\n## ・{formatted_time} {title}\n```\n{body}\n```"

    return None


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


# Botを起動
bot.run(TOKEN)
