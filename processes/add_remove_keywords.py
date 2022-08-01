import discord
from processes import Process
from database import DB, Character
from util import error_embed, success_embed, character_embed, \
    keyword_input_task, yes_no_edit_react_task, Response, Logger
from settings import Settings
from points import PointsManager

# allows for contest staff to add/remove keywords from any character
class AddRemoveKeywords(Process):
    def __init__(self, bot: discord.Client, user: discord.Member, contest_id: int, character_id: int, is_add: bool):
        super().__init__(bot, user, contest_id)
        self.character_id = character_id
        self.is_add = is_add
        self.old_char = None
        self.keywords = []

    async def start(self):
        return await self.show_current_character()

    # displays info for target character
    async def show_current_character(self):
        self.old_char: Character = DB.get_character_by_id(self.character_id)
        if not self.old_char:
            return await self.user.send(embed=error_embed("That character doesn't exist."))

        title_embed = discord.Embed(title="Current Character:")
        embed = character_embed(self.old_char)
        await self.user.send(embed=title_embed)
        await self.user.send(embed=embed)
        return await self.keyword_menu()

    # allows user to input keywords to add/remove
    async def keyword_menu(self):
        embed = discord.Embed(title="Keywords Entry")
        embed.add_field(
            name="Instructions",
            value='''
            Using this [document]({}) as reference, input keywords that should be **{}**.

            {} - Cancel Submission

            (You have **15 minutes** to complete this.)
            '''.format(Settings.points_reference_url, ("added" if self.is_add else "removed"), Settings.reject_emoji), inline=False)
        msg = await self.user.send(embed=embed)
        response = await keyword_input_task(self.bot, msg, self.user, 60.0*15)
        if type(response) is not Response:
            self.keywords = PointsManager.parse_keywords(response)
            return await self.confirm_keywords_menu()
        elif response == Response.REJECT:
            return await self.cancelled()
        else:
            assert(response == Response.TIMEDOUT)
            return await self.timed_out()

    # allows user to confirm that these are the keywords they want to add/remove
    async def confirm_keywords_menu(self):
        if not self.is_add:
            rejected_kw: set[str] = self.old_char.delta_keywords(
                set(self.keywords))
            accepted_kw: set[str] = self.old_char.keywords_intersection(
                set(self.keywords))
        else:
            rejected_kw: set[str] = self.old_char.keywords_intersection(
                set(self.keywords))
            accepted_kw: set[str] = self.old_char.delta_keywords(
                set(self.keywords))

        rejected_kw_str = str(rejected_kw) if rejected_kw else "**NONE**"
        accepted_kw_str = str(accepted_kw) if accepted_kw else "**NONE**"

        embed = discord.Embed(title="Confirm Keywords")
        embed.add_field(
            name="Accepted Keywords:",
            value="`{}`".format(accepted_kw_str),
            inline=False
        )
        if rejected_kw_str:
            embed.add_field(
                name="Rejected Keywords",
                value='''
                These keywords were rejected since the character {}:
                `{}`
                '''.format(rejected_kw_str, "already has them" if self.is_add else "doesn't already have them"),
                inline=False
            )

        embed.add_field(
            name="Instructions",
            value='''
            {} - Confirm keywords
            {} - Input keywords again
            {} - Cancel 

            (You have **5 minutes** to complete this.)
            '''.format(Settings.accept_emoji, Settings.edit_emoji, Settings.reject_emoji), inline=False)

        msg = await self.user.send(embed=embed)
        response = await yes_no_edit_react_task(self.bot, msg, self.user, 60.0*5)

        if response == Response.ACCEPT:
            self.keywords = accepted_kw
            return await self.finished()
        elif response == Response.REJECT:
            return await self.cancelled()
        elif response == Response.EDIT:
            return await self.keyword_menu()
        else:
            assert(response == Response.TIMEDOUT)
            return await self.timed_out()

    # update database with new keywords
    # send receipt of actions
    # log in server's log channel
    async def finished(self):
        if self.is_add:
            DB.add_keywords(self.character_id, set(self.keywords))
            await self.user.send(embed=success_embed("Added:\n`{}`".format(self.keywords)))
            return await Logger.added_keywords(self.user, self.bot.get_user(self.old_char.user_id), self.character_id, list(self.keywords))
        else:
            DB.remove_keywords(self.character_id, set(self.keywords))
            await self.user.send(embed=success_embed("Removed:\n`{}`".format(self.keywords)))
            return await Logger.removed_keywords(self.user, self.bot.get_user(self.old_char.user_id), self.character_id, list(self.keywords))
