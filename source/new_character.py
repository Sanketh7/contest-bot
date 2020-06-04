import discord
import asyncio
import database as db
from util import error_embed, success_embed


class NewCharacter:
    def __init__(self, bot: discord.Client, user: discord.User, class_reacts: dict, guild_id: str, contest_id: int):
        self.bot = bot
        self.user = user
        self.class_reacts = class_reacts
        self.guild_id = guild_id
        self.contest_id = contest_id

        self.class_name = "" # resolved in class selection menu

    async def start_process(self):
        has_char = await db.has_current_character(self.contest_id, self.user.id)
        if has_char:
            await self.previous_char_menu()
        else:
            await self.class_select_menu()

    async def timed_out_response(self):
        await self.user.send(embed=error_embed("Uh oh! You did not respond in time so the process timed out."))

    async def cancelled_response(self):
        await self.user.send(embed=success_embed("Cancelled."))

    async def success_response(self):
        await self.user.send(embed=success_embed("Character created."))

    async def do_class_reacts(self, dm_msg: discord.Message):
        for e in self.class_reacts.values():
            await dm_msg.add_reaction(e)
        await dm_msg.add_reaction("❌")

    async def do_confirm_reacts(self, dm_msg):
        for e in ["✅", "❌"]:
            await dm_msg.add_reaction(e)

    async def previous_char_menu(self):
        old_char = await db.get_character(self.contest_id, self.user.id)
        if not old_char:
            return
        if "class" not in old_char or "points" not in old_char:
            return await self.user.send(embed=error_embed("Not able to read previous submission. Please report this."))

        self.class_name = old_char["class"]
        if "keywords" in old_char:
            old_items = set(old_char["keywords"])
        else:
            old_items = set()
        old_class_name = old_char["class"]
        old_points = old_char["points"]

        if len(old_items) > 0:
            old_item_str = str(old_items)
        else:
            old_item_str = "**NONE**"

        embed = discord.Embed(title="Previous Character")
        embed.add_field(
            name="Current Character",
            value=
            '''
            Class: **{}**
            Items/Achievements: `{}`
            Points: **{}**
            '''.format(old_class_name, old_item_str, old_points)
        )
        embed.add_field(
            name="Instructions",
            value=
            '''
            You already have a character for this contest (shown below).
            **Creating a new character will ERASE this old character.**

            ✅ - Continue to create a character.
            ❌ - Cancel

            (You have **5 minutes** to complete this.)
            ''', inline=False
        )

        dm_msg = await self.user.send(embed=embed)
        react_task = asyncio.create_task(self.do_confirm_reacts(dm_msg=dm_msg))
        await asyncio.sleep(0)

        valid_reacts = ["✅", "❌"]

        def check(react_got: discord.Reaction, user_got: discord.User):
            return user_got.id == self.user.id and (str(react_got) in valid_reacts)

        try:
            reaction, user2 = await self.bot.wait_for('reaction_add', timeout=(60.0*5), check=check)
        except asyncio.TimeoutError:
            await react_task
            await self.timed_out_response()
        else:
            await react_task
            if str(reaction) == "❌":
                return await self.cancelled_response()
            await self.class_select_menu()

    async def class_select_menu(self):
        embed = discord.Embed(title="Class Selection")
        embed.add_field(
            name="Instructions",
            value=
            '''
            Below are all the classes available for this contest. Select a class by reacting to the emoji.
            
            ❌ - Cancel
            
            (You have **5 minutes** to complete this.)
            ''', inline=False
        )
        dm_msg = await self.user.send(embed=embed)
        react_task = asyncio.create_task(self.do_class_reacts(dm_msg=dm_msg))
        await asyncio.sleep(0)

        def check(react_got: discord.Reaction, user_got: discord.User):
            return user_got.id == self.user.id and (str(react_got) in self.class_reacts.values() or str(react_got) == "❌")

        try:
            reaction, user2 = await self.bot.wait_for('reaction_add', timeout=(60.0*5), check=check)
        except asyncio.TimeoutError:
            await react_task
            await self.timed_out_response()
        else:
            await react_task
            if str(reaction) == "❌":
                return await self.cancelled_response()
            self.class_name = next((name for name, emoji_str in self.class_reacts.items() if emoji_str == str(reaction)), None)

            await db.create_character(self.contest_id, self.user.id, self.class_name)
            await self.success_response()