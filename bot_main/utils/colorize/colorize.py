import logging
import discord
from discord.ext import tasks
import asyncio
import colorsys
import os

from dotenv import load_dotenv



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

RAINBOW_COLORS = generate_gradient_colors(steps=2)


class Colorize:
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord-bot')


    @tasks.loop(seconds=1)  # безопасный интервал
    async def rainbow_role(self, role: discord.Role):
        """Меняет цвет роли каждые 15 секунд"""
        for color in RAINBOW_COLORS:
            try:
                await role.edit(color=color, reason="Gradient rainbow effect")
                await asyncio.sleep(5)
            except Exception as e:
                self.logger.error("Rate limit или ошибка:", e)
                await asyncio.sleep(30)
