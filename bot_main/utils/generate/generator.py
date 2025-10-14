import discord
from dotenv import load_dotenv
import os
import requests
import io
import logging
import base64

load_dotenv()

HF_TOKEN = os.getenv("HF")
MODEL_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen-Image-Edit"

HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

class Generator:
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("discord-bot")

    async def generate(self, interaction: discord.Interaction, prompt: str, reference: discord.Attachment):
        self.logger.debug(f"Generating: {prompt}")

        # Считываем изображение и кодируем в base64
        image_bytes = await reference.read()
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        payload = {
            "inputs": prompt,
            "image": image_b64
        }

        try:
            response = requests.post(MODEL_URL, headers=HEADERS, json=payload)
        except Exception as e:
            await interaction.followup.send(f"Ошибка запроса: {e}")
            return

        if response.status_code != 200:
            await interaction.followup.send(f"Ошибка: {response.text}")
            return

        # Ответ приходит в base64
        try:
            result_json = response.json()
            output_b64 = result_json.get("generated_image", None)
            if not output_b64:
                await interaction.followup.send("Ошибка: модель не вернула изображение")
                return

            output_bytes = base64.b64decode(output_b64)
            await interaction.followup.send(file=discord.File(io.BytesIO(output_bytes), "result.png"))
        except Exception as e:
            await interaction.followup.send(f"Ошибка обработки ответа: {e}")
