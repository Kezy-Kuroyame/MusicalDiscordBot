import discord
from discord.ext import commands
import os
import config
import logging

from bot_main.static.ids import BIOSWIN_GUILD_ID

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("bot_main/bot.log", encoding="utf-8"),   # Запись в файл
        logging.StreamHandler()                                     # Печать в консоль
    ]
)
logger = logging.getLogger("discord-bot")
discord_logger = logging.getLogger("discord")
discord_logger.setLevel(logging.WARNING)

logger.info("Starting bot")

intents = discord.Intents.default()
intents.members = True                                              # on_member_join, roles, guild.members
intents.presences = True                                            # статус онлайн/оффлайн
intents.message_content = True                                      # обязательно для чтения сообщений

bot = commands.Bot(command_prefix=config.PREFIX, intents=intents)

async def load_modules():
    # Загружаем модули
    for filename in os.listdir("bot_main/modules"):
        if filename.endswith(".py") and filename != "__init__.py":
            try:
                logger.info(f"Trying setup module {filename}")
                await bot.load_extension(f"bot_main.modules.{filename[:-3]}")
                logger.info(f"Loaded module {filename[:-3]}")
            except Exception as e:
                logger.error(f"Failed to load module {filename}: {e}")
                exit(1)

@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user}")


@bot.event
async def setup_hook():
    await load_modules()

bot.run(config.TOKEN)