import time

import discord
from discord import Embed, Colour


async def join_voice_channel(interaction: discord.Interaction, bot):
    if not interaction.user.voice:
        await interaction.response.send_message("Братанчик, ты должен быть в голосовом канале")
        return

    channel = interaction.user.voice.channel
    voice_client = discord.utils.get(bot.voice_clients, guild=interaction.guild)

    if not voice_client:
        return await channel.connect()
    elif voice_client.channel != channel:
        await voice_client.move_to(channel)

    return voice_client


def format_progress_bar(current: int, total: int, length: int = 50) -> str:
    if total == 0:
        return "[------------------------------]"

    filled_length = int(length * current // total)
    bar = '•' * filled_length + '-' * (length - filled_length)
    return f"[{bar}]"


def create_queue_embed(queue, player):
    def _current_position(start_time):
        if start_time is None:
            return 0
        return int(time.time() - start_time)

    embed = Embed(
            title="**Поставка шмали**",
            colour=Colour.green()
        )

    embed.set_image(url=queue[0]["thumbnail"])
    embed.add_field(
        name=f"Сейчас играет:",
        value=f"[{queue[0]['title']}]({queue[0]['webpage_url']})\n" +
              f"Длительность: {formated_duration(_current_position(player.start_time))}/{formated_duration(queue[0].get('duration', '??'))}\n" +
              f"{format_progress_bar(_current_position(player.start_time), queue[0]['duration'])}",
        inline=False
    )

    for i, track in enumerate(queue):
        title = track["title"]
        if len(title) > 50:
            title = title[:47] + "..."
        if i != 0:
            embed.add_field(
                name=f"",
                value=f"{i + 1}. [{title}]({track['webpage_url']})\nДлительность: {formated_duration(track.get('duration', '??'))}",
                inline=False
            )
    return embed


def formated_duration(seconds) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)

    if h:
        return f"{h:02}:{m:02}:{s:02}"
    else:
        return f"{m}:{s:02}"