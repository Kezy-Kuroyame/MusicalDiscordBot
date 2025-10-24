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

def generate_gradient_colors(start_hex="#19d2eb", end_hex="#eb3219", steps=100):
    """Создаёт плавный градиент между двумя цветами (туда и обратно)"""
    # Конвертация HEX → RGB
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    start_rgb = hex_to_rgb(start_hex)
    end_rgb = hex_to_rgb(end_hex)

    colors = []

    # Прямой переход start → end
    for i in range(steps):
        t = i / (steps - 1)
        r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * t)
        g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * t)
        b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * t)
        colors.append(discord.Color.from_rgb(r, g, b))

    # Обратный переход end → start
    for i in range(steps):
        t = i / (steps - 1)
        r = int(end_rgb[0] + (start_rgb[0] - end_rgb[0]) * t)
        g = int(end_rgb[1] + (start_rgb[1] - end_rgb[1]) * t)
        b = int(end_rgb[2] + (start_rgb[2] - end_rgb[2]) * t)
        colors.append(discord.Color.from_rgb(r, g, b))

    return colors

RAINBOW_COLORS = [
    discord.Color.random(),
    discord.Color.random(),
    discord.Color.random(),
    discord.Color.random(),
    discord.Color.random(),
    discord.Color.random(),
    discord.Color.random(),
    discord.Color.random(),
    discord.Color.random(),
    discord.Color.random(),
    discord.Color.random(),
]


class Colorize:
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord-bot')
        self.color_cycle = cycle(RAINBOW_COLORS)

    # -----------------------------------
    # Max request: 1000, reset-time: 70 sec
    # -----------------------------------

    @tasks.loop(seconds=0)  # безопасный интервал
    async def rainbow_role(self, role):
        await asyncio.sleep(len(RAINBOW_COLORS) * 70)

        for i in range(len(RAINBOW_COLORS)):
            color = next(self.color_cycle)
            try:
                # ограничиваем edit 10 секундами
                await asyncio.wait_for(
                    role.edit(color=color, reason="Gradient rainbow effect"),
                    timeout=10
                )
                self.logger.info(f"Изменение цвета роли на: {color}")
                await asyncio.sleep(0.5)
            except asyncio.TimeoutError:
                self.logger.warning("Rate-limit!: достиг rate-limit для изменения цвета.")
