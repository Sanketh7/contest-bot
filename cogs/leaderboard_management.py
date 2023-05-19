import discord
from discord import app_commands
from discord.ext import commands, tasks
from tabulate import tabulate
from settings import Settings
from database import DB
from leaderboard import Leaderboard
from util import error_embed, success_embed, is_admin
from util import Logger

class LeaderboardManagement(commands.GroupCog, name="leaderboard"):
    def __init__(self, bot):
        self.bot = bot
        self.update_leaderboard_loop.start()
    
    def cog_unload(self):
        self.update_leaderboard_loop.cancel()

    @app_commands.command(name="full", description="Generate a complete leaderboard for a contest.")
    @is_admin()
    async def get_full_leaderboard(self, ctx, contest_id: int):
        characters = DB.get_top_characters(contest_id, None)
        guild = Settings.guild
        table = []
        prev_points = float('inf')
        place = 0
        for character in characters:
            if character.points == 0:
                break
            player = guild.get_member(character.user_id)
            if not player:
                continue
            ign = player.display_name
            if character.points >= prev_points:  # continue with same place
                table.append(
                    [None, ign, character.points, character.rotmg_class, str(
                        Settings.accept_emoji) if character.is_active else " "]
                )
            else:
                place += 1
                table.append(
                    [place, ign, character.points, character.rotmg_class, str(
                        Settings.accept_emoji) if character.is_active else " "]
                )
        table_str = tabulate(
                table, headers=["Rank", "Player", "Points", "Class", "Active?"])
        with open("full_leaderboard.txt", "w") as file:
            file.write(table_str)
        with open("full_leaderboard.txt", "rb") as file:
            await ctx.send("Full leaderboard: ", file=discord.File(file, "full_leaderboard.txt"))
    
    @app_commands.command(name="update", description="Generate a complete leaderboard for a contest.")
    @is_admin()
    async def update_leaderboard(self, ctx):
        if not DB.is_contest_running():
            return await ctx.channel.send(embed=error_embed("No contests are active."))

        await Leaderboard.update()
        await Leaderboard.display(self.bot)
        await ctx.channel.send(embed=success_embed("Leaderboard updated."))
        return await Logger.updated_leaderboard(ctx.author)

    @tasks.loop(minutes=1)
    async def update_leaderboard_loop(self):
        if DB.is_contest_running():
            await Leaderboard.update()
            await Leaderboard.display(self.bot)