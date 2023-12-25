import discord
from processes import Process
import logging
from database import DB, Character
from util import success_embed, error_embed, character_embed, Response, \
    yes_no_react_task, keyword_input_task, proof_upload_task, yes_no_edit_react_task
from settings import Settings
from points import PointsManager
from typing import Set

# allows the user to add items to their character
class EditCharacter(Process):
    def __init__(self, bot: discord.Client, user: discord.User, contest_id: int, confirm_character: bool):
        super().__init__(bot, user, contest_id)

        self.old_char: Character = None  # resolved in self.show_old_char_menu()
        self.img_url = ""  # resolved in self.proof_menu()
        self.keywords = ""  # resolved in self.keyword_menu()
        self.confirm_character = confirm_character

    # starts the process and checks if the user even has a character to edit
    async def start(self):
        self.old_char: Character = DB.get_character(
            self.contest_id, self.user.id)
        if self.old_char:
            if self.confirm_character:
                return await self.show_old_char_menu()
            else:
                return await self.show_old_char_menu_no_confirm()
        else:
            return await self.user.send(embed=error_embed("You don't have a character to edit."))
    
    async def show_old_char_menu_no_confirm(self):
        title_embed = discord.Embed(title="Current Character:")
        embed = character_embed(self.old_char)
        await self.user.send(embed=title_embed)
        await self.user.send(embed=embed)
        return await self.proof_menu()

    # shows the user their old character and confirms if they want to edit it
    async def show_old_char_menu(self):
        title_embed = discord.Embed(title="Current Character:")
        embed = character_embed(self.old_char)
        embed.add_field(
            name="Instructions:",
            value='''
            React {} to confirm you want to edit this character, {} to cancel.

            (You have **5 minutes** to complete this.)
            '''.format(Settings.accept_emoji, Settings.reject_emoji), inline=False)

        await self.user.send(embed=title_embed)
        msg = await self.user.send(embed=embed)
        response = await yes_no_react_task(self.bot, msg, self.user, 60.0*5)
        if response == Response.ACCEPT:
            return await self.proof_menu()
        elif response == Response.REJECT:
            return await self.cancelled()
        else:
            assert(response == Response.TIMEDOUT)
            return await self.timed_out()

    # prompts the user to send proof for their submission items
    # bot only responds if the response is an image attachment
    # refer to proof_upload_task() for more details on handling responses
    async def proof_menu(self):
        embed = discord.Embed(
            title="Submission for class `{}`.".format(self.old_char.rotmg_class))
        embed.add_field(
            name="Instructions",
            value='''
            Use this [document]({}) for a list of items and achievements.

            Send a message with a screenshot **in this DM** as specified in the contest rules.
            Click the **plus button** next to where you type a message to attach an image \
            or **copy and paste** an image into the message box.
            If you do not use either of the methods above, the bot **cannot** detect it.

            **You MUST have your ENTIRE game screenshotted (i.e. not just your inventory).**
            If you don't follow these rules, your submission will likely be denied.

            {} - Cancel Submission

            (You have **15 minutes** to complete this.)
            '''.format(Settings.points_reference_url, Settings.reject_emoji), inline=False)
        msg = await self.user.send(embed=embed)
        response = await proof_upload_task(self.bot, msg, self.user, 60.0*15)

        if type(response) is str:
            self.img_url = response
            return await self.keyword_menu()
        elif response == Response.REJECT:
            return await self.cancelled()
        else:
            assert(response == Response.TIMEDOUT)
            return await self.timed_out()

    # prompts the user to input the keywords corresponding to their submission
    # keywords are processed by PointsManager
    async def keyword_menu(self):
        embed = discord.Embed(title="Keywords Entry")
        embed.add_field(
            name="Instructions",
            value='''
            Using this [document]({}) as reference, enter the keywords that correspond to your items/achievements.
            This is how you will get your points.

            **If points are not entered correctly, your submission will be denied.**

            {} - Cancel Submission

            (You have **15 minutes** to complete this.)
            '''.format(Settings.points_reference_url, Settings.reject_emoji), inline=False)
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

    # finds which keywords are new 
    # keywords already in the character are rejected keywords
    # keywords that are new are accepted keywords
    async def confirm_keywords_menu(self):
        rejected_kw: Set[str] = self.old_char.keywords_intersection(
            set(self.keywords))
        accepted_kw: Set[str] = self.old_char.delta_keywords(
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
                These keywords were rejected since your character already has them:
                `{}`
                '''.format(rejected_kw_str),
                inline=False
            )

        embed.add_field(
            name="Instructions",
            value='''
            {} - Confirm keywords and **confirm submission**
            {} - Input keywords again
            {} - Cancel submission

            (You have **5 minutes** to complete this.)
            '''.format(Settings.accept_emoji, Settings.edit_emoji, Settings.reject_emoji), inline=False)

        msg = await self.user.send(embed=embed)
        response = await yes_no_edit_react_task(self.bot, msg, self.user, 60.0*5)

        if response == Response.ACCEPT:
            self.keywords = accepted_kw
            return await self.upload_submission()
        elif response == Response.REJECT:
            return await self.cancelled()
        elif response == Response.EDIT:
            return await self.keyword_menu()
        else:
            assert(response == Response.TIMEDOUT)
            return await self.timed_out()

    # sends submission embed to the server's submission channel (used to accept/reject submission)
    async def upload_submission(self):
        member: discord.Member = discord.utils.get(
            Settings.guild.members, id=self.user.id)
        if member is None:
            logging.error("Member not in guild. Aborting submission.")
            return

        delta_points = self.old_char.delta_points(self.keywords)

        if not delta_points:
            return await self.user.send(embed=error_embed("Your submission was not submitted since you did not add any points."))

        embed = discord.Embed(title="{}\t({})".format(
            member.display_name, self.old_char.rotmg_class))
        embed.add_field(name="Items/Achievements",
                        value="`{}`".format(str(self.keywords)), inline=False)
        embed.add_field(
            name="Points", value="**{}**".format(str(delta_points)), inline=False)
        embed.add_field(name="Proof", value="[image]({})".format(
            str(self.img_url)), inline=False)
        embed.set_image(url=self.img_url)

        self.post = await Settings.submission_channel.send(embed=embed)
        await self.post.add_reaction(Settings.accept_emoji)
        await self.post.add_reaction(Settings.reject_emoji)

        await self.finished()

    # adds submission to database
    # gives user receipt of submission (with submission ID)
    # process ends here
    async def finished(self):
        self.dead = True
        DB.add_submission(self.contest_id, self.user.id,
                          self.post.id, list(self.keywords), self.img_url)
        return await self.user.send(embed=success_embed(
            '''
            Submission submitted.
            You will be notified soon if your submission is accepted.

            **ID:** `{}`
            (The acceptance/rejection message will contain this ID.)
            '''.format(self.post.id)
        ))
