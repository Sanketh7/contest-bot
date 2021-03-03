import discord
import typing
import logging
from tabulate import tabulate
from discord.ext import commands, tasks
from datetime import datetime
from database import DB, Contest
from util import error_embed, success_embed, contest_post_embed, is_admin
from settings import Settings
from typing import List


class Scheduling(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.bot = bot

    @commands.command()
    @is_admin()
    async def schedule_contest(self, ctx, start_time_str: str, end_time_str: str):
        try:
            start_time = datetime.strptime(start_time_str, "%m/%d/%y %H:%M")
            end_time = datetime.strptime(end_time_str, "%m/%d/%y %H:%M")
        except ValueError:
            return await ctx.channel.send(embed=error_embed("Invalid time input."))

        DB.schedule_contest(start_time, end_time)

        return await ctx.channel.send(embed=success_embed(
            "Contest added.\nStart time (UTC): {}\nEnd time (UTC): {}".format(
                start_time_str, end_time)
        ))

    @commands.command()
    @is_admin()
    async def remove_contest(self, ctx, contest_id: int):
        DB.remove_contest(contest_id)
        return await ctx.channel.send(embed=success_embed(
            "Contest removed (if it existed). Use `+view_schedule` to view scheduled contests."))

    @commands.command()
    @is_admin()
    async def view_schedule(self, ctx):
        schedule: List[Contest] = DB.get_schedule()
        if not schedule:
            return await ctx.channel.send(embed=error_embed("No upcoming contests."))

        table = []
        for contest in schedule:
            start_time_str = contest.start_time.strftime("%m/%d/%y %H:%M")
            end_time_str = contest.end_time.strftime("%m/%d/%y %H:%M")
            table.append([str(contest.id), start_time_str, end_time_str])

        embed = discord.Embed(title="Upcoming Contests", color=0x00FF00)
        embed.description = "All times are in UTC."
        table_str = tabulate(table, headers=["ID", "Start Time", "End Time"])
        embed.add_field(name="Schedule", value="```{}```".format(
            table_str), inline=False)

        return await ctx.channel.send(embed=embed)

    @commands.command()
    @is_admin()
    async def refresh_schedule(self, ctx):
        if DB.get_current_contest():
            return await ctx.channel.send(embed=error_embed("A contest is already active."))
        if not DB.get_ready_contest():
            return await ctx.channel.send(embed=error_embed("No new contests to start."))
        return await self.start_contest_from_schedule()

    @commands.command()
    @is_admin()
    async def end_contest(self, ctx):
        if not DB.get_current_contest():
            return await ctx.channel.send(embed=error_embed("No contests are active right now."))
        await self.handle_end_contest()
        return await ctx.channel.send(embed=error_embed("Contest forcefully ended."))

    async def start_contest_from_schedule(self):
        contest: Contest = DB.get_ready_contest()
        if not contest:
            return

        embed = contest_post_embed(contest.end_time)

        post = await Settings.sign_up_channel.send(embed=embed)

        DB.start_contest(contest.id, post.id)

        await post.add_reaction(Settings.accept_emoji)
        await post.add_reaction(Settings.grave_emoji)
        await post.add_reaction(Settings.edit_emoji)

    async def handle_end_contest(self):
        contest: Contest = DB.get_current_contest()
        assert(contest and contest.should_end)

        try:
            msg = await Settings.sign_up_channel.fetch_message(contest.post_id)
            await msg.delete()
        except Exception as e:
            logging.error("Failed to delete post for contest {}\n".format(
                contest.id) + str(e))

        DB.end_current_contest()

    @tasks.loop(seconds=60)
    async def schedule_loop(self):
        contest = DB.get_current_contest()
        if contest:
            if contest.should_end:
                self.handle_end_contest()
        else:
            if DB.get_ready_contest():
                await self.start_contest_from_schedule()
