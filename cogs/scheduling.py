import discord
import logging
from tabulate import tabulate
from discord import app_commands
from discord.ext import commands, tasks
from datetime import datetime
from database import DB, Contest
from util import error_embed, success_embed, contest_post_embed, is_admin
from settings import Settings
from typing import List


class Scheduling(commands.GroupCog, name="schedule"):
    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.schedule_loop.start()

    def cog_unload(self):
        self.schedule_loop.stop()

    @app_commands.command(name="add", description="Add a contest.")
    @is_admin()
    async def schedule_contest(self, interaction: discord.Interaction, start_time_str: str, end_time_str: str):
        try:
            start_time = datetime.strptime(start_time_str, "%m/%d/%y %H:%M")
            end_time = datetime.strptime(end_time_str, "%m/%d/%y %H:%M")
        except ValueError:
            return await interaction.response.send_message(embed=error_embed("Invalid time input."))

        DB.schedule_contest(start_time, end_time)

        return await interaction.response.send_message(embed=success_embed(
            "Contest added.\nStart time (UTC): {}\nEnd time (UTC): {}".format(
                start_time, end_time)
        ))

    @app_commands.command(name="remove", description="Remove a contest.")
    @is_admin()
    async def remove_contest(self, interaction: discord.Interaction, contest_id: int):
        DB.remove_contest(contest_id)
        return await interaction.response.send_message(embed=success_embed(
            "Contest removed (if it existed). Use `/schedule view` to view scheduled contests."))

    @app_commands.command(name="view", description="View contest schedule.")
    @is_admin()
    async def view_schedule(self, interaction: discord.Interaction):
        schedule: List[Contest] = DB.get_schedule()
        if not schedule:
            return await interaction.response.send_message(embed=error_embed("No upcoming contests."))

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

        return await interaction.response.send_message(embed=embed)

    @app_commands.command(name="refresh", description="Refresh the contest schedule.") 
    @is_admin()
    async def refresh_schedule(self, interaction: discord.Interaction):
        if DB.get_current_contest():
            return await interaction.response.send_message(embed=error_embed("A contest is already active."))
        if not DB.get_ready_contest():
            return await interaction.response.send_message(embed=error_embed("No new contests to start."))
        await self.start_contest_from_schedule()
        return await interaction.response.send_message(embed=success_embed("Refreshed schedule."))

    @app_commands.command(name="end", description="End an active contest.") 
    @is_admin()
    async def end_contest(self, interaction: discord.Interaction):
        if not DB.get_current_contest():
            return await interaction.response.send_message(embed=error_embed("No contests are active right now."))
        await self.handle_end_contest()
        return await interaction.response.send_message(embed=error_embed("Contest forcefully ended."))

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
        # assert(contest and contest.should_end)

        try:
            msg = await Settings.sign_up_channel.fetch_message(contest.post_id)
            await msg.delete()
        except Exception as e:
            logging.error("Failed to delete post for contest {}\n".format(
                contest.id) + str(e))

        DB.end_current_contest()

    @tasks.loop(seconds=10)
    async def schedule_loop(self):
        contest = DB.get_current_contest()
        if contest:
            if contest.should_end:
                await self.handle_end_contest()
        else:
            if DB.get_ready_contest():
                await self.start_contest_from_schedule()
