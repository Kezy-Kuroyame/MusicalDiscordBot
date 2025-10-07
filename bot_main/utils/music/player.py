import asyncio
import logging
import queue
import time
from collections import deque
from symtable import Class

import discord
import yt_dlp
from discord import app_commands

from bot_main.utils.music import track_select_view
from bot_main.utils.music.helpers import join_voice_channel, formated_duration


class Player:
    def __init__(self, bot):
        self.bot = bot
        self.queues: dict[int, deque] = {}
        self.logger = logging.getLogger("discord-bot")
        self.ydl_opts_autocomplete = {
            "quiet": True,
            "extract_flat": True,
            "skip_download": True,
        }
        self.ydl_opts = {
            'quiet': True,
            "default_search": "ytsearch5",
            "noplaylist": True,
            'skip_download': True,
            'format': 'm4a/bestaudio/best',
            "writesubtitles": False,  # не загружать субтитры
            "writeautomaticsub": False,
        }
        self.start_time = None
        self.ydl = yt_dlp.YoutubeDL(self.ydl_opts)
        self.ydl_fast = yt_dlp.YoutubeDL(self.ydl_opts_autocomplete)

        self._search_task = None   # фоновая задача поиска


    # ------------------------------
    # Очередь
    # ------------------------------

    def get_queue(self, guild_id):
        self.logger.debug(f"Getting queue for guild {guild_id}")
        if guild_id in self.queues:
            return self.queues[guild_id]
        return deque()

    def add_queue(self, guild_id, track_info):
        if guild_id not in self.queues:
            self.queues[guild_id] = deque()
        self.queues[guild_id].append(track_info)


    # ------------------------------
    # Быстрый поиск для выбора трека
    # ------------------------------

    async def _search_youtube_async(self, query: str):
        """Фоновый поиск для подсказок"""

        def _extract():
            info = self.ydl_fast.extract_info(f"ytsearch5:{query}", download=False)
            entries = info.get("entries", [])
            logging.info(f"entries: {entries[:5]}")

            return entries[:5]

        results = await asyncio.to_thread(_extract)
        self._last_results = results
        self._last_query = query
        return results


    async def get_autocomplete(self, interaction: discord.Interaction, query: str):
        """Запускает фоновый поиск"""
        self.logger.debug("get_autocomplete")

        results = await self._search_youtube_async(query)

        # Создаём Embed с результатами
        embed = discord.Embed(title=f"Результаты поиска: {query}", color=discord.Color.green())
        for i, track in enumerate(results, 1):
            logging.info(f"[{i}/{len(results)}] {track}")
            embed.add_field(
                name=f"",
                value=(
                    f"{i}. **[{track['title']}]({track['url']})** - ({formated_duration(track['duration'])})"
                ),
                inline=False)

        view = track_select_view.TrackSelectView(results, self)

        # Редактируем сообщение
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


    # ------------------------------
    # Основной поиск для play
    # ------------------------------

    async def search_youtube(self, query: str):
        self.logger.debug("search_youtube")
        self.logger.info(f"Searching youtube with query: {query}")

        def _extract():
            info = self.ydl.extract_info(f"ytsearch1:{query}", download=False)
            entries = info.get("entries", [])
            logging.info(f"entries: {entries[0]}")
            return entries[0]


        results = await asyncio.to_thread(_extract)
        return results


    # ------------------------------
    # Логика воспроизведения
    # ------------------------------

    async def play_next(self, interaction: discord.Interaction, voice_client):
        logging.debug("play_next")
        if not self.get_queue(interaction.guild.id):
            return
        await self.player(interaction, voice_client)


    async def play_logic(self, interaction: discord.Interaction, query: str):
        self.logger.debug("play_logic")

        voice_client = await join_voice_channel(interaction, self.bot)

        if not voice_client:
            return

        track_info = await self.search_youtube(query)

        if not track_info:
            await interaction.followup.send("Бля я нихуя не нашёл по твоему запросу")
            return

        # logging.info(f"track_info: {track_info['title'], track_info['duration'], track_info['thumbnail']}")
        self.add_queue(interaction.guild.id, track_info)
        if voice_client.is_playing():
            await interaction.followup.send(f"Шмальнул в очередь: **{track_info['title']}**")
            return
        else:
            await interaction.followup.send(f"dasdas")
            await self.player(interaction, voice_client)


    async def player(self, interaction, voice_client):

        self.logger.debug("player")
        track_info = self.queues[interaction.guild.id][0]
        self.logger.info(f"track_info: {track_info}")

        ffmpeg_opts = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }

        source = discord.FFmpegPCMAudio(track_info['url'], **ffmpeg_opts)
        source = discord.PCMVolumeTransformer(source, volume=0.05)

        def after_playing(error):
            self.logger.debug("after_playing")
            if voice_client.is_playing():
                voice_client.stop()
            if interaction.guild.id in self.queues and self.queues[interaction.guild.id] and track_info == self.queues[interaction.guild.id][0]:
                self.queues[interaction.guild.id].popleft()
            if error:
                self.logger.error(f"Ошибка при попытке проиграть следующий трек: {error}")
            if interaction.guild.id in self.queues and self.queues[interaction.guild.id]:
                coroutine = self.play_next(interaction, voice_client)
                fut = asyncio.run_coroutine_threadsafe(coroutine, self.bot.loop)
                fut.add_done_callback(lambda f: f.exception())
            else:
                return


        self.logger.debug("checking playing")
        self.start_time = time.time()
        self.logger.info(f"start_time: {self.start_time}, source: {source}")
        voice_client.play(source, after=after_playing)

        await interaction.followup.send(f"Сейчас ебашит: [{track_info['title']}]({track_info['webpage_url']})")
