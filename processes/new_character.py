import discord
import logging
from processes import Process
from util import success_embed, character_embed
from settings import Settings
from database import DB
from util import yes_no_react_task, rotmg_class_select_task, Response


class NewCharacter(Process):
    def __init__(self, bot: discord.Client, user: discord.User, contest_id: int):
        super().__init__(bot, user, contest_id)
        self.rotmg_class = ""  # resolved in self.class_select_menu()

    async def start(self):
        has_char = DB.get_character(self.contest_id, self.user.id) is not None
        if has_char:
            return await self.previous_char_menu()
        else:
            return await self.class_select_menu()

    async def finished(self):
        self.dead = True
        DB.new_character(self.contest_id, self.user.id, self.rotmg_class)
        return await self.user.send(embed=success_embed("Character created."))

    async def previous_char_menu(self):
        old_char: DB.db.Character = DB.get_character(
            self.contest_id, self.user.id)
        if not old_char:
            logging.error(
                "Failed to get the old character for user " + str(self.user.id))
            return

        title_embed = discord.Embed(title="Previous Character")
        embed = character_embed(old_char)
        embed.add_field(
            name="Instructions",
            value='''
            You already have a character for this contest (shown above).
            **Creating a new character will prevent you from adding items to this old character.**

            {} - Continue to create a character.
            {} - Cancel

            (You have **5 minutes** to complete this.)
            '''.format(Settings.accept_emoji, Settings.reject_emoji),
            inline=False)

        await self.user.send(embed=title_embed)
        msg = await self.user.send(embed=embed)
        response = await yes_no_react_task(self.bot, msg, self.user, 60.0*5)
        if response == Response.ACCEPT:
            return await self.class_select_menu()
        elif response == Response.REJECT:
            return await self.cancelled()
        else:
            assert(response == Response.TIMEDOUT)
            return await self.timed_out()

    async def class_select_menu(self):
        embed = discord.Embed(title="Class Selection")
        embed.add_field(
            name="Instructions",
            value='''
            Below are all the classes available for this contest. Select a class by reacting to the emoji.

            {} - Cancel

            (You have **5 minutes** to complete this.)
            '''.format(Settings.reject_emoji), inline=False)

        msg = await self.user.send(embed=embed)
        response = await rotmg_class_select_task(self.bot, msg, self.user, 60.0*5)
        if isinstance(response, str):
            self.rotmg_class = response
            return await self.finished()
        elif response == Response.REJECT:
            return await self.cancelled()
        else:
            assert(response == Response.TIMEDOUT)
            return await self.timed_out()
