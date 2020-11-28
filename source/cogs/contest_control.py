import discord
from discord.ext import commands
from datetime import datetime
import source.constants as constants
from source.database.database import DB
from tabulate import tabulate
from source.util import Logger, success_embed, error_embed
from source.leaderboard import Leaderboard
from source.cache import Cache
from typing import List
from source.payloads import *


# TODO: update the permissions for these commands
class ContestControl(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.bot: discord.Client = bot

    @commands.command('add_contest')
    async def add_contest(self, ctx, contest_type: str, start_time_str: str, end_time_str: str):
        if contest_type not in constants.CONTEST_TYPES:
            return await ctx.send(embed=error_embed("Invalid contest type."))

        try:
            start_time = datetime.strptime(start_time_str, "%m/%d/%y %H:%M")
            end_time = datetime.strptime(end_time_str, "%m/%d/%y %H:%M")
        except ValueError:
            return await ctx.send(embed=error_embed("Invalid time inputs."))

        start_time = start_time.timestamp()
        end_time = end_time.timestamp()

        DB.add_contest_to_schedule(contest_type, start_time, end_time)

        start_time_str = datetime.utcfromtimestamp(float(start_time)).strftime("%m/%d/%y %H:%M")
        end_time_str = datetime.utcfromtimestamp(float(end_time)).strftime("%m/%d/%y %H:%M")

        return await ctx.send(embed=success_embed("Contest added.\nStart Time: {}\nEnd Time: {}"
                                                  .format(start_time_str, end_time_str)))

    @commands.command('remove_contest')
    async def remove_contest(self, ctx, contest_id: int):
        res: bool = DB.remove_contest_from_schedule(contest_id)
        if res:
            return await ctx.send(embed=success_embed("Contest removed."))
        return await ctx.send(embed=error_embed("Contest not found."))

    @commands.command('end_contest')
    async def end_contest(self, ctx):
        if Cache.is_contest_active:
            ch: discord.TextChannel = discord.utils.get(self.bot.get_guild(Cache.guild.id).text_channels, name=SIGN_UP_CHANNELS)
            try:
                msg = await ch.fetch_message(Cache.contest_post_id)
                await msg.delete()
            except:
                await ctx.send(embed=error_embed("Failed to retrieve/delete contest post."))

            res: bool = DB.check_and_deactivate_current_contest()
            if res:
                await ctx.send(embed=success_embed("Contest manually ended."))
            else:
                await ctx.send(embed=error_embed("Database error: could not find contest."))

            await self.remove_contest_role()
        else:
            await ctx.send(embed=error_embed("No active contest to end."))

    @commands.command('view_schedule')
    async def view_schedule(self, ctx):
        schedule: List[ContestPayload] = DB.get_scheduled_contests()
        if len(schedule) == 0:
            return await ctx.send(embed=success_embed("No upcoming contests."))

        table = []
        for contest in schedule:
            start_time_str = datetime.utcfromtimestamp(float(contest.start_time)).strftime("%m/%d/%y %H:%M")
            end_time_str = datetime.utcfromtimestamp(float(contest.end_time)).strftime("%m/%d/%y %H:%M")
            table.append([str(contest.id), contest.contest_type_name, start_time_str, end_time_str])

        embed = discord.Embed(title="Upcoming Contests", color=0x00FF00)
        embed.description = "All times are in UTC."
        table_str = tabulate(table, headers=["ID", "Contest Type", "Start Time", "End Time"])
        embed.add_field(name="Schedule", value="```{}```".format(str(table_str)), inline=False)

        await ctx.send(embed=embed)

    @commands.command('refresh_schedule')
    async def refresh_schedule(self, ctx):
        if Cache.is_contest_active:
            return await ctx.send(embed=error_embed("A contest is already active."))

        res: bool = DB.check_and_activate_scheduled_contest()
        if res:
            # TODO: start contest
            return await ctx.send(embed=success_embed("Contest started."))
        else:
            return await ctx.send(embed=error_embed("No new contest to start."))

    async def contest_schedule_loop(self):
        while True:
            # end current contest if it's done
            if Cache.is_contest_active:
                res: bool = DB.check_and_deactivate_current_contest()
                post_id: int = Cache.contest_post_id

                if res:  # contest removed
                    ch: discord.TextChannel = discord.utils.get(self.bot.get_guild(Cache.guild.id).text_channels, name=SIGN_UP_CHANNEL)

                    try:
                        msg: discord.Message = await ch.fetch_message(post_id)
                        await msg.delete()
                    except:
                        print("Failed to retrieve/delete contest post.")

                    await self.remove_contest_role()

            # start new contest if it is time to do so
            elif not Cache.is_contest_active:
                await start_new


    async def create_contest_post(self, contest_type: str, end_time: float) -> discord.Message:
        end_time = datetime.utcfromtimestamp(end_time)
        embed = discord.Embed(title="A New `{}` Contest Has Started!".format(contest_type.upper()))
        embed.description = "Ends on {} at {} (UTC).".format(f'{end_time:%B %d, %Y}', f'{end_time:%H:%M}')
        embed.add_field(
            name="Instructions",
            value=
            '''
            ✅ - Sign up for the contest. (Let's you view all the channels and submit.)
            {} - Start a new character. Completing this will STOP your previous character (so you can't edit it anymore).
            ✏ - Edit a character. This will add items/achievements to your current character.

            Use the command `+profile` to view all your characters for this contest.
            '''.format(GRAVESTONE_EMOJI),
            inline=False
        )

        ch: discord.TextChannel = discord.utils.get(self.bot.get_guild(Cache.guild.id).text_channels,
                                                    name=SIGN_UP_CHANNEL)
        post: discord.Message = await ch.send(embed=embed)

        await post.add_reaction("✅")
        await post.add_reaction(GRAVESTONE_EMOJI)
        await post.add_reaction("✏")

        return post

    async def start_new_contest(self):
        if contest_type not in constants.CONTEST_TYPES:
            return

        if not DB.check_scheduled_contest():  # no contest
            return

        post: discord.Message = await self.create_contest_post(contest_type, end_time)
        res: bool = DB.check_and_activate_scheduled_contest(post.id)




    async def remove_contest_role(self):
        role: discord.Role = discord.utils.get(self.bot.get_guild(Cache.guild.id).roles, name=IN_CONTEST_ROLE)
        members: List[discord.Member] = role.members
        for member in members:
            await member.remove_roles(role)
            
    # force_refresh_schedule
    # force_update_leaderboard
    # view_schedule
    # not a command: start contest, start_new_contest_from_schedule, contest_schedule_loop