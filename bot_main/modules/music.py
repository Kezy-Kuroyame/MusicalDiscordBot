import logging
import traceback

import discord

from discord import app_commands
from discord.ext import commands
from collections import deque

from bot_main.utils.music.player import Player


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("discord-bot")
        self.player = Player(bot)
        self.queues: dict[int, deque] = {}


    # --- Slash команды ---
    @app_commands.command(name="play", description="Включить трек с ютуба")
    async def play(self, interaction: discord.Interaction, *, query: str):
        self.logger.debug(f"play command with query: {query}")
        try:
            await interaction.response.defer(thinking=True)
            await self.player.play_logic(interaction, query=query)
        except Exception as e:
            self.logger.error(f"Команда play вызвала ошибку: {e}\ntraceback: {traceback.format_exc()}")

    @app_commands.command(name="skip", description="Пропустить текущий трек")
    async def skip(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        try:
            if voice_client and voice_client.is_playing():
                voice_client.stop()
                await interaction.response.send_message("Ну и нахуй этот трек реально")
            else:
                await interaction.response.send_message("Ёбнулся? И так ничё не играет")
        except Exception as e:
            self.logger.error(f"Команда skip вызвала ошибку: {e}\ntraceback: {traceback.format_exc()}")

    @app_commands.command(name="queue", description="Посмотреть очередь треков")
    async def queue(self, interaction: discord.Interaction):
        try:
            queue = self.player.get_queue(interaction.guild.id)
            if not queue:
                await interaction.response.send_message("Бля, запамятовал. А стоп ты не добавлял треков в очередь, шиз")
                return

            msg = "Ну вот такие треки в очереди:\n" + "\n".join([f"{i + 1}. {q}" for i, q in enumerate(queue)])
            await interaction.response.send_message(msg)
        except Exception as e:
            self.logger.error(f"Команда queue вызвала ошибку: {e}\ntraceback: {traceback.format_exc()}")


async def setup(bot):
    await bot.add_cog(Music(bot))