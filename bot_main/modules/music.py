import yt_dlp
import discord
from discord import app_commands
from discord.ext import commands
from youtubesearchpython import VideosSearch

from bot_main.utils.helpers import joinVoiceChannel


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def search_youtube(self, query: str):
        ydl_opts = {'quiet': True, 'extract_flat': True, 'skip_download': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)
            if info['entries']:
                return info['entries'][0]['url']
        return None

    async def _play_logic(self, interaction: discord.Interaction, query: str):
        voice_client = await joinVoiceChannel(interaction, self.bot)

        if not voice_client:
            return

        url = await self.search_youtube(query)
        if not url:
            await interaction.response.send("Бля я нихуя не нашёл по твоему запросу")
            return

        ytdl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'extractaudio': True,
        }

        ytdl = yt_dlp.YoutubeDL(ytdl_opts)
        info = ytdl.extract_info(url, download=False)
        audio_url = info['url']

        ffmpeg_opts = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        source = discord.FFmpegPCMAudio(audio_url, **ffmpeg_opts)
        source = discord.PCMVolumeTransformer(source, volume=0.02)

        if voice_client.is_playing():
            voice_client.stop()
        voice_client.play(source)

        await interaction.response.send(f"Сейчас ебашит: {info['title']}")


    @app_commands.command(name="play", description="Включить трек с ютуба")
    async def play(self, interaction: discord.Interaction, *, query: str):
        await self._play_logic(interaction, query)


async def setup(bot):
    await bot.add_cog(Music(bot))