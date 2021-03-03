import discord
import typing
from discord.ext import commands
from database import DB
from util import error_embed, success_embed, character_embed, user_busy_embed, is_contest_staff
from processes import ProcessManager, AddRemoveKeywords, BusyException, NewCharacter, EditCharacter
from settings import Settings


class UserManagement(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.bot = bot

    @commands.command()
    async def profile(self, ctx, other_user: typing.Optional[discord.Member] = None):
        if not DB.is_contest_running():
            return await ctx.send(embed=error_embed("No contests are active."))

        user: discord.Member = other_user if other_user else ctx.author
        assert(user)

        embeds = [discord.Embed(
            title="{}'s Characters".format(user.display_name))]

        char_list = DB.get_characters_by_user(
            DB.get_current_contest_id(), user.id)

        embeds += [character_embed(c) for c in char_list]
        for e in embeds:
            await ctx.author.send(embed=e)

    @commands.command()
    @is_contest_staff()
    async def remove_items(self, ctx, char_id: int):
        try:
            return await ProcessManager.spawn(ctx.author.id, AddRemoveKeywords(
                self.bot, ctx.author, DB.get_current_contest_id(), char_id, False))
        except BusyException:
            return await ctx.author.send(embed=user_busy_embed())

    @commands.command()
    @is_contest_staff()
    async def add_items(self, ctx, char_id: int):
        try:
            return await ProcessManager.spawn(ctx.author.id, AddRemoveKeywords(
                self.bot, ctx.author, DB.get_current_contest_id(), char_id, True))
        except BusyException:
            return await ctx.author.send(embed=user_busy_embed())

    @commands.command()
    @is_contest_staff()
    async def ban(self, ctx, user: discord.Member):
        if not DB.is_contest_running():
            return await ctx.send(embed=error_embed("No active contest to ban from."))
        if not user:
            return await ctx.send(embed=error_embed("Invalid user."))

        DB.ban_user(DB.get_current_contest_id(), user.id)
        # TODO: log

    @commands.command()
    @is_contest_staff()
    async def unban(self, ctx, user: discord.Member):
        if not DB.is_contest_running():
            return await ctx.send(embed=error_embed("No active contest to unban from."))
        if not user:
            return await ctx.send(embed=error_embed("Invalid user."))

        DB.unban_user(DB.get_current_contest_id(), user.id)
        # TODO: log

    @commands.command()
    @is_contest_staff()
    async def view_bans(self, ctx):
        if not DB.is_contest_running():
            return await ctx.send(embed=error_embed("No active contest."))
        data = DB.get_ban_list(DB.get_current_contest_id())
        mentions = []
        for i in data:
            user = self.bot.get_user(int(i))
            if not user:
                continue
            mentions.append(user.mention)
        mention_str = '\n'.join(i for i in mentions)
        return await ctx.send(embed=success_embed("Banned users:\n " + mention_str))

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        try:
            user: discord.User = self.bot.get_user(payload.user_id)
            member: discord.Member = Settings.guild.get_member(payload.user_id)
        except Exception:
            return
        if user == self.bot.user or not user:
            return

        if not DB.is_contest_running():
            return

        is_on_contest_post = DB.get_contest_post_id() == payload.message_id
        if not is_on_contest_post:
            return

        if payload.emoji == Settings.grave_emoji:
            if Settings.contestant_role not in member.roles:
                return await user.send(embed=error_embed("You need to sign up before you can submit or edit a character."))
            try:
                return await ProcessManager.spawn(payload.user_id, NewCharacter(
                    self.bot, user, DB.get_current_contest_id()))
            except BusyException:
                return await user.send(embed=user_busy_embed())
        elif str(payload.emoji) == Settings.edit_emoji:
            if Settings.contestant_role not in member.roles:
                return await user.send(embed=error_embed("You need to sign up before you can submit or edit a character."))
            try:
                return await ProcessManager.spawn(payload.user_id, EditCharacter(
                    self.bot, user, DB.get_current_contest_id()))
            except BusyException:
                return await user.send(embed=user_busy_embed())
        elif str(payload.emoji) == Settings.accept_emoji:
            if Settings.contestant_role not in member.roles:
                await member.add_roles(Settings.contestant_role)
                return await user.send(embed=success_embed("You are now part of the contest. Good luck!"))
