import logging
from itertools import cycle

import aiohttp
import discord
from discord.ext import tasks
import asyncio
import colorsys
import os

from dotenv import load_dotenv

load_dotenv()
ROLE_ID = int(os.getenv('ROLE_ID'))
GUILD_ID = int(os.getenv('BIOSWIN_GUILD_ID'))
TOKEN = os.getenv('TOKEN')


RAINBOW_COLORS = [
    discord.Color.from_rgb(30, 227, 155),
    discord.Color.from_rgb(30, 227, 178),
    discord.Color.from_rgb(30, 227, 194),
    discord.Color.from_rgb(30, 220, 227),
    discord.Color.from_rgb(30, 158, 227),
    discord.Color.from_rgb(30, 220, 227),
    discord.Color.from_rgb(30, 227, 194),
    discord.Color.from_rgb(30, 227, 178),
    discord.Color.from_rgb(30, 227, 155),
]


class Colorize:
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord-bot')
        self.color_cycle = cycle(RAINBOW_COLORS)

    async def change_role_color(self, color):
        url = f"https://discord.com/api/v10/guilds/{GUILD_ID}/roles/{ROLE_ID}"
        headers = {"Authorization": f"Bot {TOKEN}", "Content-Type": "application/json"}
        json_data = {"color": color.value}

        async with aiohttp.ClientSession() as session:
            async with session.patch(url, headers=headers, json=json_data) as resp:
                if resp.status == 429:  # rate limit
                    data = await resp.json()
                    retry_after = data.get("retry_after", 5)
                    self.logger.info(f"Rate limit! Жду {retry_after} сек...")
                    await asyncio.sleep(retry_after)
                elif resp.status in (200, 204):
                    self.logger.info(f"Цвет роли изменён: {color.value:#06x}")
                else:
                    self.logger.warning(f"Ошибка {resp.status}: {await resp.text()}")


    async def rainbow_role(self, role):
        while True:
            color = next(self.color_cycle)
            await self.change_role_color(color)
            await asyncio.sleep(70)


