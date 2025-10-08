import logging

import discord
from discord.types import embed
from discord.ui import View, Button


class TrackSelectView(View):
    def __init__(self, tracks, player):
        super().__init__()
        self.player = player
        self.tracks = tracks 
        self.logger = logging.getLogger("discord-bot")

        # Добавляем кнопки для каждого трека
        for i, track in enumerate(tracks, 1):
            button = Button(label=f"{i}", style=discord.ButtonStyle.primary, custom_id=f"track_{i}")
            button.callback = self.create_callback(track)
            self.add_item(button)

    def create_callback(self, track):
        async def callback(interaction: discord.Interaction):
            self.logger.debug(f"callback on track {track['title']}")
            self.stop()
            await interaction.message.delete()
            await self.player.play_logic(interaction=interaction, query=track['url'], track=track)

        return callback