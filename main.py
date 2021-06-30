import logging
import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from cogs import Scheduling, ContestManagement, UserManagement
from settings import Settings
from points import PointsManager


def main():
    load_dotenv()
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    DB_FILE = os.getenv('DB_FILE')

    intents = discord.Intents.default()
    intents.members = True

    bot = commands.Bot(command_prefix="+", intents=intents)

    @bot.event
    async def on_ready():
        print(f'{bot.user.name} has connected!')

        Settings.reload_all(bot)

        PointsManager.parse_data()

        bot.add_cog(Scheduling(bot))
        bot.add_cog(ContestManagement(bot))
        bot.add_cog(UserManagement(bot))

    bot.run(DISCORD_TOKEN)


if __name__ == '__main__':
    main()
