import discord


async def joinVoiceChannel(interaction: discord.Interaction, bot):
    if not interaction.user.voice:
        await interaction.response.send("Братанчик, ты должен быть в голосовом канале")
        return

    channel = interaction.user.voice.channel
    voice_client = discord.utils.get(bot.voice_clients, guild=interaction.guild)

    if not voice_client:
        return await channel.connect()
    elif voice_client.channel != channel:
        await voice_client.move_to(channel)