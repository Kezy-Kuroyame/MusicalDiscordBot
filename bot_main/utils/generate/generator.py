import discord
import logging
import aiohttp
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
import os
import json
import base64

load_dotenv()
DF = os.getenv('DF')  # твой API-ключ stablediffusionapi.com

class Generator:
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("discord-bot")
        self.api_url = "https://modelslab.com/api/v7/images/image-to-image"

    async def generate(self, interaction: discord.Interaction, prompt: str, reference: discord.Attachment):
        try:

            # читаем изображение друга
            img_bytes = await reference.read()
            img_b64 = base64.b64encode(img_bytes).decode("utf-8")

            payload = {
                "init_image": f"data:image/png;base64,{img_b64}",
                "prompt": prompt,
                "model_id": "seededit-i2i",
                "key": DF
            }

            headers = {"Content-Type": "application/json"}

            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, headers=headers, json=payload) as resp:
                    if resp.status != 200:
                        text = await resp.text()
                        raise ValueError(f"Modelslab API error: {resp.status} - {text}")
                    result = await resp.json()

            # результат приходит в base64
            self.logger.info(json.dumps(result, indent=2))
            output_b64 = result["image"]
            output_bytes = base64.b64decode(output_b64)
            image = Image.open(BytesIO(output_bytes))

            with BytesIO() as image_binary:
                image.save(image_binary, "PNG")
                image_binary.seek(0)
                await interaction.followup.send(file=discord.File(fp=image_binary, filename="generated.png"))

        except Exception as e:
            self.logger.exception("Ошибка при генерации через Modelslab API")
