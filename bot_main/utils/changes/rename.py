from dotenv import load_dotenv
import os
import asyncio
import discord
import aiohttp


load_dotenv()
KEZY_ID = os.getenv('KEZY_ID')

class Rename:
    def __init__(self, bot):
        self.bot = bot

# -----------------------------------
# Max request: 10, reset-time: 10 sec
# -----------------------------------

    async def rename(self, user_id, list_names):
        pass

