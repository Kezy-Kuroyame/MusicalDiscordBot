import logging
import traceback

import discord

from discord import app_commands
from discord.ext import commands
from collections import deque


from bot_main.utils.music.player import Player
from bot_main.utils.music.helpers import create_queue_embed


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("discord-bot")
        self.player = Player(bot)


    # ------------------------------
    # --- Slash команды ---
    # ------------------------------

    @app_commands.command(name="play", description="Включить трек с ютуба")
    async def play(self, interaction: discord.Interaction, *, query: str):
        self.logger.debug(f"play command with query: {query}")
        try:
            # await interaction.response.defer(thinking=True)
            await self.player.get_autocomplete(interaction, query=query)
        except Exception as e:
            self.logger.error(f"Команда play вызвала ошибку: {e}\ntraceback: {traceback.format_exc()}")

    @app_commands.command(name="skip", description="Пропустить текущий трек")
    async def skip(self, interaction: discord.Interaction):
        self.logger.debug(f"Команда skip")
        voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
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
        self.logger.debug(f"Команда queue")
        try:
            queue = self.player.get_queue(interaction.guild.id)
            self.logger.info(f"Треки в очереди: {queue}")
            if not queue:
                await interaction.response.send_message("Бля, запамятовал. А стоп ты не добавлял треков в очередь, шиз")
                return

            embed = create_queue_embed(queue, self.player)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            self.logger.error(f"Команда queue вызвала ошибку: {e}\ntraceback: {traceback.format_exc()}")

    @app_commands.command(name="loop", description="Повтор всех добавленных треков")
    async def loop(self, interaction: discord.Interaction):
        self.logger.debug(f"Команда loop")
        voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        try:
            if not self.player.is_loop:
                self.player.is_loop = True
                await interaction.response.send_message("А ты шаришь за loop у")
            else:
                self.player.is_loop = False
                await interaction.response.send_message("Бля, больше не шарю за loop у")

        except Exception as e:
            self.logger.error(f"Команда skip вызвала ошибку: {e}\ntraceback: {traceback.format_exc()}")

    @app_commands.command(name="repeat", description="Повтор одного трека")
    async def repeat(self, interaction: discord.Interaction):
        self.logger.debug(f"Команда repeat")
        try:
            if not self.player.is_repeat:
                self.player.is_repeat = True
                await interaction.response.send_message("Ебанул репитика")
            else:
                self.player.is_repeat = False
                await interaction.response.send_message("Вырубил репитик")
        except Exception as e:
            self.logger.error(f"Команда skip вызвала ошибку: {e}\ntraceback: {traceback.format_exc()}")

    @app_commands.command(name="volume", description="Изменить громкость (0-100%) [стандарт: 5]")
    async def volume(self, interaction: discord.Interaction, level: int):
        self.logger.debug(f"Команда volume, уровень: {level}%")
        try:
            self.player.set_volume(interaction, level)
            await interaction.response.send_message(
                f"🔊 Громкость установлена на **{level}%**",
                ephemeral=False
            )

        except PermissionError as e:
            await interaction.response.send_message(f"❌ {e}", ephemeral=True)
        except ValueError as e:
            await interaction.response.send_message(f"⚠️ {e}", ephemeral=True)
        except Exception as e:
            self.logger.error(f"Ошибка в команде volume: {e}\ntraceback: {traceback.format_exc()}")
            await interaction.response.send_message("❌ Не удалось изменить громкость.", ephemeral=True)

    @app_commands.command(name="bass", description="Изменить уровень басса (-10 до 20 дБ) [стандарт: 0]")
    async def bass(self, interaction: discord.Interaction, level: int):
        self.logger.debug(f"Команда bass, уровень: {level} дБ")
        try:
            self.player.set_bass(interaction, level)
            await interaction.response.send_message(
                f"🎧 Басс установлен на **{level} дБ**",
                ephemeral=False
            )

        except PermissionError as e:
            await interaction.response.send_message(f"❌ {e}", ephemeral=True)
        except ValueError as e:
            await interaction.response.send_message(f"⚠️ {e}", ephemeral=True)
        except Exception as e:
            self.logger.error(f"Ошибка в команде bass: {e}\ntraceback: {traceback.format_exc()}")
            await interaction.response.send_message("❌ Не удалось изменить уровень басса.", ephemeral=True)

    @app_commands.command(name="history", description="Показать последние 15 треков")
    async def history(self, interaction: discord.Interaction):
        self.logger.debug("Вызов команды /history")
        try:
            await self.player.show_history(interaction)
        except Exception as e:
            self.logger.error(f"Ошибка при вызове /history: {e}")
            await interaction.response.send_message("Не удалось получить историю треков.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Music(bot))