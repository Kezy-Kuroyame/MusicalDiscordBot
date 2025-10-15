import logging

from discord.ext import commands
from discord import app_commands
import discord
import os
import traceback

from dotenv import load_dotenv
from bot_main.utils.generate.generator import Generator
from bot_main.utils.colorize.colorize import Colorize


load_dotenv()
ROLE_ID = int(os.getenv('ROLE_ID'))
GUILD_ID = int(os.getenv('BIOSWIN_GUILD_ID'))

class Fun(commands.Cog):
    def __init__(self, bot):
        self.logger = logging.getLogger("discord-bot")
        self.bot = bot
        self.generator = Generator(bot)
        self.colorize = Colorize(bot)


    @app_commands.command(name="hello", description="Приветствие от бота")
    async def hello(self, interaction: discord.Interaction):
        self.logger.debug("Command - Hello")
        await interaction.response.send_message(f"ахахаха ШМАЛЬ, {interaction.user.mention}")


    @app_commands.command(name="image", description="Создаёт изображение с бароном Емельяновым")
    async def image(self, interaction: discord.Interaction, prompt: str, reference: discord.Attachment):
        self.logger.debug("Command - Image")
        await interaction.response.defer(thinking=True)
        try:
            await self.generator.generate(interaction, prompt, reference)
        except Exception as e:
            self.logger.error(f"Команда play вызвала ошибку: {e}\ntraceback: {traceback.format_exc()}")


    @commands.Cog.listener()
    async def on_ready(self):
        """Запускается при старте бота"""
        self.logger.debug("Start Rainbow role")
        await self.bot.wait_until_ready()

        guild = self.bot.get_guild(GUILD_ID)
        role = guild.get_role(ROLE_ID)
        await self.colorize.rainbow_role(role)


async def setup(bot):
    await bot.add_cog(Fun(bot))
