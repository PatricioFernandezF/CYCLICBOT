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



async def inicializar():

    # Load variables from .env file if present
    load_dotenv()

    # Read the variable from the environment (or .env file)
    
    secret_token = os.getenv("SECRET_TOKEN")
    TOKEN = os.getenv('comfyapi')
    WORKFLOW=os.getenv('workflow')
    webhook_url = os.getenv('CYCLIC_URL', 'http://localhost:8181') + "/webhook/"

    print(bot)
    await bot.set_webhook(url=webhook_url)
    webhook_info = bot.get_webhook_info()
    print(webhook_info)



app = FastAPI()
bot_token = os.getenv('BOT_TOKEN')
bot = Bot(token=bot_token)
inicializar()


def auth_telegram_token(x_telegram_bot_api_secret_token: str = Header(None)) -> str:
    # return true # uncomment to disable authentication
    return True
    if x_telegram_bot_api_secret_token != secret_token:
        raise HTTPException(status_code=403, detail="Not authenticated")
    return x_telegram_bot_api_secret_token

@app.post("/webhook/")
async def handle_webhook(update: TelegramUpdate, token: str = Depends(auth_telegram_token)):
    chat_id = update.message["chat"]["id"]
    text = update.message["text"]
    print("Received message:", update.message)

    if text == "/start":
        with open('hello.gif', 'rb') as photo:
            await bot.send_photo(chat_id=chat_id, photo=photo)
        await bot.send_message(chat_id=chat_id, text="¡Hola! Soy un bot de Telegram. Pon /prompt + el prompt")
    else:
        if "/prompt" in text:
            prompt=text.replace("/prompt ","")
            await bot.send_message(chat_id=chat_id, text="Procesando Prompt: "+prompt)
            api_key = TOKEN
            comfy_api = ComfyDeployAPI(api_key)
            workflow_id = WORKFLOW
            run_response = await comfy_api.run_workflow(workflow_id,{"input_text":prompt})
            print(run_response)

            # Ejemplo de cómo obtener la salida de la ejecución de un workflow
            

            run_id = run_response["run_id"] # Reemplaza con el run_id real obtenido después de ejecutar el workflow
            #update["chat"].update({'run_id':run_id})

            #print(update["chat"]["run_id"])
    
            try:
                if run_id:
                    output_response = await comfy_api.get_workflow_run_output(run_id)
                    print(output_response)
                    
                    image_info = output_response.get('outputs', [{}])[0].get('data', {}).get('images', [{}])[0]
                    image_url = image_info.get('url')
                
                    if image_url:
                        await bot.send_photo(chat_id=chat_id, photo=image_url)
                    else:
                        await bot.send_message(chat_id=chat_id, text="Ha habido un error con el prompt")
                        return {"ok": True}
            except:
                await bot.send_message(chat_id=chat_id, text="Ha habido un error con el prompt")
                return {"ok": True}  
                
        else:
            await bot.send_message(chat_id=chat_id, text="Recuerda que solo estoy programado para recibir /prompt")

    return {"ok": True}


