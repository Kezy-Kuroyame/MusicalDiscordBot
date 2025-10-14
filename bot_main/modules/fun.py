import logging

from discord.ext import commands
from discord import app_commands
import discord

from bot_main.utils.generate.generator import Generator
import traceback



class Fun(commands.Cog):
    def __init__(self, bot):
        self.logger = logging.getLogger("discord-bot")
        self.bot = bot
        self.generator = Generator(bot)


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


async def setup(bot):
    await bot.add_cog(Fun(bot))
