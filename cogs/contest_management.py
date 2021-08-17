import discord
import logging
from discord.ext import commands, tasks
from datetime import datetime
from database import DB, Contest, Submission
from util import error_embed, success_embed, contest_post_embed, is_admin
from settings import Settings
from leaderboard import Leaderboard
from util import Logger


class ContestManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_leaderboard_loop.start()

    def cog_unload(self):
        self.update_leaderboard_loop.cancel()

    @commands.command()
    @is_admin()
    async def change_end_time(self, ctx, end_time_str: str):
        if not DB.is_contest_running():
            return await ctx.channel.send(embed=error_embed("No contests are active."))

        contest: Contest = DB.get_current_contest()

        try:
            end_time = datetime.strptime(end_time_str, "%m/%d/%y %H:%M")
        except ValueError:
            return await ctx.channel.send(embed=error_embed("Invalid time input."))

        DB.change_end_time(end_time)

        await ctx.channel.send(embed=success_embed(
            "Contest now runs until (UTC): {}".format(end_time_str)
        ))

        embed = contest_post_embed(end_time)

        try:
            msg = await Settings.sign_up_channel.fetch_message(contest.post_id)
            await msg.edit(embed=embed)
        except Exception as e:
            logging.error("Failed to change contest post for contest {}\n".format(
                contest.id) + str(e))

    @commands.command()
    @is_admin()
    async def update_leaderboard(self, ctx):
        if not DB.is_contest_running():
            return await ctx.channel.send(embed=error_embed("No contests are active."))

        await Leaderboard.update()
        await Leaderboard.display(self.bot)
        await ctx.channel.send(embed=success_embed("Leaderboard updated."))
        return await Logger.updated_leaderboard(ctx.author)

    @tasks.loop(minutes=2)
    async def update_leaderboard_loop(self):
        if DB.is_contest_running():
            await Leaderboard.update()
            await Leaderboard.display(self.bot)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        try:
            user: discord.User = self.bot.get_user(payload.user_id)
            member: discord.Member = Settings.guild.get_member(payload.user_id)
        except Exception:
            return
        if user == self.bot.user or not user:
            return

        if payload.channel_id != Settings.submission_channel.id:
            return

        if str(payload.emoji) == Settings.accept_emoji:
            # Accept submission
            submission, user_id = DB.accept_submission(payload.message_id)
            if not submission:
                return
            try:
                msg = await Settings.submission_channel.fetch_message(payload.message_id)
                await msg.delete()
                other_user = self.bot.get_user(user_id)
                await other_user.send(embed=success_embed("You submission with ID `{}` was accepted!".format(submission.post_id)))
                return await Logger.accepted_submission(user, submission)
            except Exception as e:
                logging.error(
                    "Failed to delete submission message and/or notify user.\n" + str(e))
                return

        elif str(payload.emoji) == Settings.reject_emoji:
            # Reject submission
            submission, user_id = DB.get_submission(payload.message_id)
            if not submission:
                return
            try:
                msg = await Settings.submission_channel.fetch_message(payload.message_id)
                await msg.delete()
                other_user = self.bot.get_user(user_id)
                await other_user.send(embed=error_embed("You submission with ID `{}` was denied!".format(submission.post_id)))
                return await Logger.rejected_submission(user, submission)
            except Exception as e:
                logging.error(
                    "Failed to delete submission message and/or notify user.\n" + str(e))
                return
