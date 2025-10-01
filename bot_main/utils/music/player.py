import asyncio
import logging
from collections import deque
from symtable import Class

import discord
import yt_dlp

from bot_main.utils.helpers import joinVoiceChannel

class Player:
    def __init__(self, bot):
        self.bot = bot
        self.queues: dict[int, deque] = {}
        self.logger = logging.getLogger("discord-bot")

    
    def get_queue(self, guild_id):
        self.logger.debug(f"Getting queue for guild {guild_id}")
        if guild_id in self.queues:
            return self.queues[guild_id]
    
    
    async def search_youtube(self, query: str):
        self.logger.debug("search_youtube")
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'format': 'bestaudio/best'
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)
            return info['entries'][0]
            # if info and "entries" in info and info["entries"]:
            #     entry = info["entries"][0]
            #     return {
            #         "url": entry["url"],
            #         "title": entry.get("title", "Unknown title"),
            #         "webpage_url": entry.get("webpage_url", f"https://www.youtube.com/watch?v={entry.get('id')}")
            #     }

    
    async def play_next(self, interaction: discord.Interaction, query: str):
        queue = self.get_queue(interaction.guild.id)
        if not queue:
            return
        queue = queue.popleft()
        await self.play_logic(interaction, queue, from_queue=True)


    async def play_logic(self, interaction: discord.Interaction, query: str, from_queue: bool = False):
        self.logger.debug("play_logic")
        voice_client = await joinVoiceChannel(interaction, self.bot)

        if not voice_client:
            return

        track_info = await self.search_youtube(query)

        if not track_info:
            await interaction.followup.send("Бля я нихуя не нашёл по твоему запросу")
            return

        logging.info(f"track_info: {track_info['title'], track_info['duration'], tr}")

        audio_url = track_info['url']

        ffmpeg_opts = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }
        source = discord.FFmpegPCMAudio(audio_url, **ffmpeg_opts)
        source = discord.PCMVolumeTransformer(source, volume=0.05)

        def after_playing(error):
            if error:
                self.logger.error(f"Ошибка при попытке проиграть следующий трек: {error}")
            coroutine = self.play_next(interaction, voice_client)
            fut = asyncio.run_coroutine_threadsafe(coroutine, self.bot.loop)
            fut.add_done_callback(lambda f: f.exception())

        self.logger.debug("checking playing")
        if voice_client.is_playing():
            queue = self.get_queue(interaction.guild.id)
            queue.append(track_info)
            if not from_queue:
                await interaction.followup.send(f"Шмальнул в очередь: **{track_info['title']}**")
            return

        voice_client.play(source, after=after_playing)
        if not from_queue:
            await interaction.followup.send(f"Сейчас ебашит: [{track_info['title']}]({track_info['webpage_url']})")
