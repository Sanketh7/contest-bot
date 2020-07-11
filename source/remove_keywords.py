import discord
from database import *
import asyncio
from flashtext import *
from util import success_embed, error_embed

class RemoveKeywords:
    def __init__(self, _bot: discord.Client, _user: discord.Member, _char_id: str, _points_doc, _keyword_data, _isRemoval: bool, _contest_id, _points_data):
        self.bot = _bot
        self.user = _user
        self.char_id = _char_id
        self.points_doc = _points_doc
        self.keyword_data = _keyword_data
        self.isRemoval = _isRemoval
        self.contest_id = _contest_id
        self.points_data = _points_data

        self.keywords = set()

    async def timed_out_response(self):
        await self.user.send(embed=error_embed("Uh oh! You did not respond in time so the process timed out."))

    async def cancelled_response(self):
        await self.user.send(embed=success_embed("Cancelled."))

    async def do_confirm_reacts(self, dm_msg):
        for e in ['✅', '❌']:
            await dm_msg.add_reaction(e)

    async def do_confirm_edit_reacts(self, dm_msg):
        for e in ['✅', '✏', '❌']:
            await dm_msg.add_reaction(e)

    async def start_process(self):
        await self.show_current_items()

    async def show_current_items(self):
        char = Database.get_character_from_uuid(self.contest_id, self.char_id)
        if char is None:
            return await self.user.send(embed=error_embed("That character doesn't exist."))

        embed = discord.Embed(title="Current Keywords:")
        if len(str(char["keywords"])) >= 800:
            curr_arr = []
            curr_len = 3
            counter = 1
            for k in char["keywords"]:
                curr_len += len(str(k)) + 3
                if curr_len >= 800:
                    embed.add_field(
                        name="More Keywords:" if counter > 1 else "Keywords:",
                        value="`{}`".format(curr_arr),
                        inline=False
                    )
                    curr_len = 0
                    curr_arr = []
                    counter += 1
                curr_arr.append(k)
            if len(curr_arr) > 0:
                embed.add_field(
                    name="More Keywords:" if counter > 1 else "Keywords:",
                    value="`{}`".format(curr_arr),
                    inline=False
                )
        else:
            embed.add_field(
                name='Keywords:',
                value="`" + str(char["keywords"]) + "`",
                inline=False
            )

        await self.user.send(embed=embed)
        await self.keyword_menu()

    async def keyword_menu(self):
        embed = discord.Embed(title="Keywords Entry")
        embed.add_field(
            name="Instructions",
            value=
            '''
            Using this [document]({}) as reference, input keywords that should be **{}**.

            ❌ - Cancel submission

            (You have **15 minutes** to complete this.)
            '''.format(self.points_doc, ("removed" if self.isRemoval else "added"))
        )
        dm_msg = await self.user.send(embed=embed)
        await dm_msg.add_reaction("❌")

        def check_msg(m: discord.Message):
            return len(m.content) > 0 and m.guild is None and m.author.id == self.user.id

        def check_react(react_got: discord.Reaction, user_got: discord.User):
            return user_got.id == self.user.id and str(react_got) == "❌"

        try:
            tasks = [
                asyncio.create_task(self.bot.wait_for('message', timeout=(60.0 * 15), check=check_msg)),
                asyncio.create_task(self.bot.wait_for('reaction_add', timeout=(60.0 * 15), check=check_react))
            ]

            for future in asyncio.as_completed(tasks):
                res = await future

                if type(res) is tuple and type(res[0]) is discord.Reaction:
                    await self.cancelled_response()
                elif type(res) is discord.Message:
                    self.parse_keywords(res.content)
                    await self.confirm_keywords_menu()

                for task in tasks:
                    task.cancel()

                return
        except asyncio.TimeoutError:
            await self.timed_out_response()

    def parse_keywords(self, data: str):
        proc = KeywordProcessor()
        proc.add_keywords_from_dict(self.keyword_data)
        items = proc.extract_keywords(data)

        self.keywords = set()
        for item in items:
            self.keywords.add(item)

    async def confirm_keywords_menu(self):
        items_str = ""
        if len(self.keywords) > 0:
            items_str = str(self.keywords)
        else:
            items_str = "**NONE**"

        embed = discord.Embed(title="Confirm Keywords")
        embed.add_field(
            name="Accepted Keywords:",
            value="`" + items_str + "`",
            inline=False
        )

        embed.add_field(
            name="Instructions",
            value='''
                    ✅ - Confirm keywords
                    ✏ - Input keywords again
                    ❌ - Cancel

                    (You have **5 minutes** to complete this.)
                    ''',
            inline=False
        )

        # TODO: forbid empty keyword list

        dm_msg = await self.user.send(embed=embed)
        valid_reactions = ['✅', '✏', '❌']
        react_task = asyncio.create_task(self.do_confirm_edit_reacts(dm_msg=dm_msg))
        await asyncio.sleep(0)

        def check(react_got: discord.Reaction, user_got: discord.User):
            return user_got.id == self.user.id and str(react_got) in valid_reactions

        try:
            reaction, user2 = await self.bot.wait_for('reaction_add', timeout=(60.0 * 5), check=check)
        except asyncio.TimeoutError:
            await react_task
            await self.timed_out_response()
        else:
            await react_task
            if str(reaction) == "❌":
                return await self.cancelled_response()
            if str(reaction) == "✏":
                return await self.keyword_menu()
            await self.make_changes()

    async def make_changes(self):
        if self.isRemoval:
            items_removed = await Database.remove_items_from_character(self.contest_id, self.char_id, self.keywords, self.points_data, self.user.id)
            await self.user.send(embed=success_embed('''The following items were removed: \n `{}`'''.format(items_removed)))
        else:
            items_added = await Database.add_items_to_character(self.contest_id, self.char_id, self.keywords, self.points_data, self.user.id)
            await self.user.send(embed=success_embed('''The following items were added: \n `{}`'''.format(items_added)))