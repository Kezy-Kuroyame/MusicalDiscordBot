import time

import discord
from discord import Embed, Colour


def format_progress_bar(current: int, total: int, length: int = 30) -> str:
    if total == 0:
        return "[------------------------------]"

    filled_length = int(length * current // total)
    bar = '*' * filled_length + '-' * (length - filled_length)
    return f"[{bar}]"


def create_queue_embed(queue, player):
    def _current_position(start_time):
        if start_time is None:
            return 0
        return int(time.time() - start_time)

    embed = Embed(
            title="Поставка шмали",
            description="Сейчас в очереди:",
            colour=Colour.green()
        )

    embed.set_image(url=queue[0]["thumbnail"])
    embed.add_field(
        name=f"Сейчас играет:",
        value=f"[{queue[0]['title']}]({queue[0]['webpage_url']})\n" +
              "Длительность: {_current_position(player.start_time)}/{queue[0].get('duration', '??')} сек\n" +
              f"{format_progress_bar(_current_position(player.start_time), queue[0]['duration'])}",
        inline=False
    )

    for i, track in enumerate(queue):
        title = track["title"]
        if len(title) > 50:
            title = title[:47] + "..."
        if i != 0:
            embed.add_field(
                name=f"{i + 1}. [{title}]({track['webpage_url']})",
                value=f"Длительность: {track.get('duration', '??')} сек",
                inline=False
            )
    return embed