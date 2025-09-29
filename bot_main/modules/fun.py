import logging

from discord.ext import commands
from discord import app_commands
import discord


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="hello", description="Приветствие от бота")
    async def hello(self, interaction: discord.Interaction):
        logging.info("Command - Hello")
        await interaction.response.send_message(f"ахахаха ШМАЛЬ, {interaction.user.mention}")

async def setup(bot):
    await bot.add_cog(Fun(bot))
