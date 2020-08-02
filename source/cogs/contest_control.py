import discord
from discord.ext import commands
from datetime import datetime
import constants
from database.database import DB
from tabulate import tabulate
from util import Logger, success_embed, error_embed
from leaderboard import Leaderboard
from cache import Cache


# TODO: update the permissions for these commands
class ContestControl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def add_contest(self, ctx, contest_type: str, start_string: str, end_string: str):
        if contest_type not in constants.CONTEST_TYPES:
            return await ctx.send(embed=error_embed("Invalid contest type."))

        try:
            start_time = datetime.strptime(start_string, "%m/%d/%y %H:%M")
            end_time = datetime.strptime(end_string, "%m/%d/%y %H:%M")
        except ValueError:
            return await ctx.send(embed=error_embed("Invalid time inputs."))

        start_time = start_time.timestamp()
        end_time = end_time.timestamp()

        DB.add_contest_to_schedule(contest_type, start_time, end_time)

        start_time_str = datetime.utcfromtimestamp(float(start_time)).strftime("%m/%d/%y %H:%M")
        end_time_str = datetime.utcfromtimestamp(float(end_time)).strftime("%m/%d/%y %H:%M")

        return await ctx.send(embed=success_embed("Contest added.\nStart Time: {}\nEnd Time: {}".format(start_time_str, end_time_str)))

    @commands.command()
    async def remove_contest(self, ctx, contest_id: int):
        res: bool = DB.remove_contest_from_schedule(contest_id)
        if not res:
            return await ctx.send(embed=error_embed("Contest not found in schedule."))
        return await ctx.send(embed=success_embed("Contest removed from schedule."))

    @commands.command()
    async def view_schedule(self, ctx):
        contests = DB.get_scheduled_contests()

        table = []
        for contest in contests:
            start_time_str = datetime.utcfromtimestamp(contest.start_time).strftime("%m/%d/%y %H:%M")
            end_time_str = datetime.utcfromtimestamp(contest.end_time).strftime("%m/%d/%y %H:%M")
            table.append([str(id), contest.contest_type_name, start_time_str, end_time_str])

        embed = discord.Embed(title="Upcoming Contests", color=0x00FF00)
        embed.description = "All times are in UTC."
        table_str = tabulate(table, headers=["ID", "Contest Type", "Start Time", "End Time"])
        embed.add_field(name="Schedule", value="```" + str(table_str) + "```", inline=False)

        return await ctx.send(embed=embed)

    @commands.command()
    async def set_points_document(self, ctx, contest_type: str, url: str):
        res = DB.set_points_document_url(contest_type, url)
        if not res:
            return await ctx.send(embed=error_embed("Invalid contest type."))
        return await ctx.send(embed=success_embed("Document set for contest type: `" + str(contest_type) + "`"))

    @commands.command()
    async def refresh_leaderboard(self, ctx):
        await Leaderboard.update()
        await Leaderboard.display()
        await ctx.send(embed="Leaderboard updated.")
        await Logger.refresh_leaderboard(ctx.author)

    @commands.command()
    async def refresh_schedule(self, ctx):
        if Cache.is_contest_active:
            return await ctx.send(embed=error_embed("A contest is already active."))

        res = await start_new_contest_from_schedule()
        if res:
            return await ctx.send(embed=success_embed("Contest started."))
        else:
            return await ctx.send(embed=error_embed("No new contest to start."))

    async def begin_contest(self):
        if not Cache.is_contest_active:
            is_contest = DB.check_scheduled_contest()
            if not is_contest:
                return False
            
        return False

    async def create_contest_post(self, contest_type: str, end_time: float):
        end_time = datetime.utcfromtimestamp(end_time)
        embed = discord.Embed(title="A New `" + contest_type.upper() + "` Contest Has Started!`")
        embed.description = "Ends on " + f"{end_time:%B %d, %Y}" + " at " + f"{end_time: %H:%M}" + " (UTC)"
        embed.add_field(
            name="Instructions",
            value=
            """
            ✅ - Sign up for the contest. (Let's you view all the channels and submit.)
        {} - Start a new character. Completing this will STOP your previous character (so you can't edit it anymore).
        ✏ - Edit a character. This will add items/achievements to your current character.
        
        Use the command `+profile` to view all your characters for this contest. 
            """.format(str())
        )

'''
@bot.command(name='add_contest')
@is_admin()
async def add_contest(ctx, contest_type: str, start_string: str, end_string: str):
    if contest_type not in contest_types:
        return await ctx.channel.send(embed=error_embed("Invalid contest type."))

    try:
        start_time = datetime.datetime.strptime(start_string, "%m/%d/%y %H:%M")
        end_time = datetime.datetime.strptime(end_string, "%m/%d/%y %H:%M")
    except ValueError:
        return await ctx.channel.send(embed=error_embed("Invalid time input."))

    # start_time = start_time.replace(tzinfo=datetime.timezone.utc).timestamp()
    # end_time = end_time.replace(tzinfo=datetime.timezone.utc).timestamp()
    start_time = start_time.timestamp()
    end_time = end_time.timestamp()
    res = Database.schedule_contest(contest_type, start_time, end_time)
    schedule_cache[res["key"]] = res["data"]

    start_time_str = datetime.datetime.utcfromtimestamp(float(start_time)).strftime("%m/%d/%y %H:%M")
    end_time_str = datetime.datetime.utcfromtimestamp(float(end_time)).strftime("%m/%d/%y %H:%M")

    await ctx.channel.send(embed=success_embed(
        "Contest added. \nStart time (UTC): {}\n End time (UTC): {}".format(start_time_str, end_time_str)
    ))
    
@bot.command(name='view_schedule')
@is_admin()
async def view_schedule(ctx):
    if not schedule_cache:
        return await ctx.channel.send(embed=error_embed("No upcoming contests."))

    table = []
    for uid, data in schedule_cache.items():
        start_time_str = datetime.datetime.utcfromtimestamp(float(data["start_time"])).strftime("%m/%d/%y %H:%M")
        end_time_str = datetime.datetime.utcfromtimestamp(float(data["end_time"])).strftime("%m/%d/%y %H:%M")
        table.append([str(uid), data["contest_type"], start_time_str, end_time_str])

    embed = discord.Embed(title="Upcoming Contests", color=0x00FF00)
    embed.description = "All times are in UTC."
    table_str = tabulate(table, headers=["ID", "Contest Type", "Start Time", "End Time"])
    embed.add_field(name="Schedule", value="```"+str(table_str)+"```", inline=False)

    await ctx.channel.send(embed=embed)
'''
