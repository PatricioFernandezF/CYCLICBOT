import os
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Depends
from telegram import Update, Bot
from pydantic import BaseModel
import asyncio
from deploy import ComfyDeployAPI
import json


class TelegramUpdate(BaseModel):
    update_id: int
    message: dict




app = FastAPI()
load_dotenv()
secret_token = os.getenv("SECRET_TOKEN")
TOKEN = os.getenv('comfyapi')
WORKFLOW=os.getenv('workflow')
bot_token = os.getenv('BOT_TOKEN')
bot = Bot(token=bot_token)
print("Inicializado")
webhook_url = os.getenv('CYCLIC_URL', 'http://localhost:8181') + "/webhook/"
print(bot)
bot.set_webhook(url=webhook_url)
webhook_info = bot.get_webhook_info()
print(webhook_info)


def auth_telegram_token(x_telegram_bot_api_secret_token: str = Header(None)) -> str:
    # return true # uncomment to disable authentication
    return True
    if x_telegram_bot_api_secret_token != secret_token:
        raise HTTPException(status_code=403, detail="Not authenticated")
    return x_telegram_bot_api_secret_token

@app.post("/webhook/")
async def handle_webhook(update: TelegramUpdate, token: str = Depends(auth_telegram_token)):
    print("Received update:", update)
    chat_id = update.message["chat"]["id"]
    text = update.message["text"]
    print("Received message:", update.message)

    if text == "/start":
        with open('hello.gif', 'rb') as photo:
            await bot.send_photo(chat_id=chat_id, photo=photo)
        await bot.send_message(chat_id=chat_id, text="¡Hola! Soy un bot de Telegram. Pon /prompt + el prompt")
    else:
 
        await bot.send_message(chat_id=chat_id, text="Recuerda que solo estoy programado para recibir /prompt")

    return {"ok": True}


