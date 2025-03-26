import discord
import os
import re
from datetime import datetime, timedelta
from discord.ext import commands
from fastapi import FastAPI
from threading import Thread
import uvicorn

app = FastAPI()

# 環境変数からトークンを取得
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Botの設定
intents = discord.Intents.default()
intents.message_content = True  # メッセージ内容の取得を許可
bot = commands.Bot(command_prefix="!", intents=intents)

# FastAPIルート
@app.get("/")
async def root():
    return {"message": "Server is Online."}

# Discord Bot用のコードをここに記載
@bot.event
async def on_message(message):
    if message.author == bot.user:  # 自分のメッセージは無視
        return
    if bot.user.mentioned_in(message):
        await message.channel.send("こんにちは！何かお手伝いしますか？")
    # 以下、現在のコードを保持

def start_discord_bot():
    bot.run(TOKEN)

def start_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=8080)

if __name__ == "__main__":
    # FastAPIとDiscord Botを並行して起動
    Thread(target=start_fastapi).start()
    start_discord_bot()
