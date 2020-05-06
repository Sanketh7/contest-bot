import discord
import database as db

class Leaderboard:
    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.top = {}  # user => points

    async def update(self):
        pass

    async def display(self):
        pass