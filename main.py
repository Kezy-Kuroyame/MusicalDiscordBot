import asyncio

import discord
from discord.ext import commands
import os
import logging
from dotenv import load_dotenv

# Загружаем .env
load_dotenv()

TOKEN = os.getenv("TOKEN")
PREFIX = os.getenv("PREFIX", "!")
BIOSWIN_GUILD_ID = int(os.getenv("BIOSWIN_GUILD_ID", 0))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///db.sqlite3")

import logging
from logging.handlers import RotatingFileHandler

# Ротация логов: максимум 10 МБ, храним 5 предыдущих файлов
file_handler = RotatingFileHandler(
    filename="bot_main/bot.log",
    mode="a",
    maxBytes=100 * 1024 * 1024,  # 10 МБ
    backupCount=2,              # хранить 5 старых логов
    encoding="utf-8",
    delay=False
)

# Потоковый вывод в консоль
stream_handler = logging.StreamHandler()

# Базовая конфигурация
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[file_handler, stream_handler]
)
logger = logging.getLogger("discord-bot")
discord_logger = logging.getLogger("discord")
discord_logger.setLevel(logging.WARNING)

logger.info("Starting bot")

intents = discord.Intents.default()
intents.members = True                                              # on_member_join, roles, guild.members
intents.presences = True                                            # статус онлайн/оффлайн
intents.message_content = True                                      # обязательно для чтения сообщений

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

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
    guild = bot.get_guild(BIOSWIN_GUILD_ID)
    logger.info(f"commands: {await bot.tree.sync(guild=guild)}")


bot.run(TOKEN)