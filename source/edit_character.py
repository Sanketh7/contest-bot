import discord
from util import error_embed, success_embed
import asyncio
from flashtext import KeywordProcessor
from database import *
import mimetypes


class EditCharacter:
    def __init__(self, bot: discord.Client, user: discord.User, guild_id: str, sub_channel_name: str,
                 keyword_data: dict, points_data: dict, contest_id: int, points_doc: str):
        self.bot = bot
        self.user = user
        self.guild_id = guild_id
        self.sub_channel_name = sub_channel_name
        self.keyword_data = keyword_data
        self.points_data = points_data
        self.contest_id = contest_id
        self.points_doc = points_doc

        self.class_name = ""
        self.img_url = ""
        self.original_user_keywords = set()
        self.original_points = 0
        self.new_points = 0
        self.submitted_user_keywords_accepted = set()  # ones that aren't duplicates of original
        self.submitted_user_keywords_rejected = set()  # removed ones already in original
        self.new_user_keywords = set()  # keywords after union of submitted and old

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
        has_char = Database.has_current_character(self.contest_id, self.user.id)
        if has_char:
            return await self.show_old_character_menu()
        else:
            return await self.user.send(embed=error_embed("You don't have a character to edit."))

    async def show_old_character_menu(self):
        old_char = Database.get_character(self.contest_id, self.user.id)
        if not old_char:
            return await self.user.send(embed=error_embed("You don't have a character to edit."))
        if "class" not in old_char or "points" not in old_char:
            return await self.user.send(embed=error_embed("Not able to read previous submission. Please report this."))

        self.class_name = old_char["class"]
        if "keywords" in old_char:
            self.original_user_keywords = set(old_char["keywords"])
            self.new_user_keywords = set(old_char["keywords"])
        else:
            self.original_user_keywords = set()
            self.new_user_keywords = set()
        self.original_points = old_char["points"]

        item_str = ""
        if len(self.original_user_keywords) > 0:
            item_str = str(self.original_user_keywords)
        else:
            item_str = "**NONE**"

        embed = discord.Embed(title="Current Character")
        embed.add_field(name="Class", value="**"+self.class_name+"**", inline=False)
        embed.add_field(name="Items/Achievements", value="`" + item_str + "`", inline=False)
        embed.add_field(name="Points", value=("**" + str(self.original_points) + "**"), inline=False)
        embed.add_field(name="Instructions", value='''
                React ✅ to confirm you want to edit this character, ❌ to cancel.

                (You have **5 minutes** to complete this.)
                ''', inline=False)
        dm_msg = await self.user.send(embed=embed)

        valid_reactions = ['✅', '❌']

        react_task = asyncio.create_task(self.do_confirm_reacts(dm_msg=dm_msg))
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
            await self.proof_menu()

    async def proof_menu(self):
        embed = discord.Embed(title="Submission for class `" + self.class_name + "`.")
        embed.add_field(
            name="Instructions",
            value=
            '''
            Use this [document]({}) for a list of items and achievements.
            
            Send a message with a screenshot **in this DM** as specified in the contest rules. 
            Click the **plus button** next to where you type a message to attach an image \
            or **copy and paste** and image into the message box.
            If you do not use either of the methods above, the bot **cannot** detect it.

            **You MUST have your ENTIRE game screenshotted (i.e. not just your inventory).**
            If you don't follow this, your submission will likely be denied.

            ❌ - cancel submission

            (You have **15 minutes** to complete this.)
            '''.format(self.points_doc),
            inline=False
        )
        dm_msg = await self.user.send(embed=embed)
        await dm_msg.add_reaction("❌")

        def is_url_image(url):
            mimetype, encoding = mimetypes.guess_type(url)
            return (mimetype and mimetype.startswith('image'))

        def check_msg(m: discord.Message):
            return len(m.attachments) > 0 and m.attachments[0].url is not None and is_url_image(m.attachments[0].url) and m.author.id == self.user.id

        def check_react(react_got: discord.Reaction, user_got: discord.User):
            return user_got.id == self.user.id and str(react_got) == "❌"

        try:
            tasks = [asyncio.create_task(self.bot.wait_for('message', timeout=(60.0 * 15), check=check_msg)),
                     asyncio.create_task(self.bot.wait_for('reaction_add', timeout=(60.0 * 15), check=check_react))]

            for future in asyncio.as_completed(tasks):
                res = await future

                if type(res) is tuple and type(res[0]) is discord.Reaction:
                    await self.cancelled_response()
                elif type(res) is discord.Message:
                    if len(res.attachments) <= 0:
                        print("hi")
                        continue
                    self.img_url = res.attachments[0].url
                    await self.keyword_menu()

                for task in tasks:
                    task.cancel()

                return
        except asyncio.TimeoutError:  # timed out
            await self.timed_out_response()

    async def keyword_menu(self):
        embed = discord.Embed(title="Keywords Entry")
        embed.add_field(
            name="Instructions",
            value=
            '''
            Using this [document]({}) as reference, enter the keywords that correspond to your items/achievements.
            This is how you will get your points.

            **If points are not entered correctly, your submission will be denied.**
            
            ❌ - Cancel submission

            (You have **15 minutes** to complete this.)
            '''.format(self.points_doc)
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

    def parse_keywords(self, data):
        proc = KeywordProcessor()
        proc.add_keywords_from_dict(self.keyword_data)
        items = proc.extract_keywords(data)

        self.new_points = 0
        self.submitted_user_keywords_accepted = set()
        self.submitted_user_keywords_rejected = set()
        self.new_user_keywords = set()

        for item in items:
            if item not in self.original_user_keywords:
                self.submitted_user_keywords_accepted.add(item)
            else:
                self.submitted_user_keywords_rejected.add(item)

        self.new_user_keywords = self.submitted_user_keywords_accepted.union(self.original_user_keywords)

        for item in self.new_user_keywords:
            self.new_points += self.points_data[item][self.class_name]

    async def confirm_keywords_menu(self):
        accepted_items_str = ""
        rejected_items_str = ""

        if len(self.submitted_user_keywords_accepted):
            accepted_items_str = str(self.submitted_user_keywords_accepted)
        else:
            accepted_items_str = "**NONE**"

        if len(self.submitted_user_keywords_rejected):
            rejected_items_str = str(self.submitted_user_keywords_rejected)

        embed = discord.Embed(title="Confirm Keywords")
        embed.add_field(
            name="Accepted Keywords:",
            value="`" + accepted_items_str + "`",
            inline=False
        )

        if rejected_items_str != "":
            embed.add_field(
                name="Rejected Keywords",
                value='''
                These keywords were rejected since your character already has them:
                `{}`
                '''.format(rejected_items_str),
                inline=False
            )

        embed.add_field(
            name="Instructions",
            value='''
            ✅ - Confirm keywords and **confirm submission**
            ✏ - Input keywords again
            ❌ - Cancel submission
            
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
            await self.upload_submission()

    async def upload_submission(self):
        member: discord.Member = discord.utils.get(self.bot.get_guild(int(self.guild_id)).members, id=self.user.id)
        if member is None:
            return

        delta_points = self.new_points - self.original_points

        if delta_points == 0:
            await self.user.send(embed=error_embed(
                '''
                Your submission was not submitted since you did not add any points.
                '''
            ))
            return

        if len(self.submitted_user_keywords_accepted) > 0:
            item_str = str(self.submitted_user_keywords_accepted)
        else:
            item_str = "**NONE**"

        embed = discord.Embed(title=member.display_name + "    (" + str(self.class_name) + ")")
        embed.add_field(name="Items/Achievements", value="`" + item_str + "`", inline=False)
        embed.add_field(name="Points", value=("**" + str(delta_points) + "**"))
        embed.set_image(url=self.img_url)

        ch: discord.TextChannel = discord.utils.get(self.bot.get_guild(int(self.guild_id)).text_channels,
                                                    name=self.sub_channel_name)

        post = await ch.send(embed=embed)
        await post.add_reaction("✅")
        await post.add_reaction("❌")




        Database.add_pending_submission(self.contest_id, post.id, int(self.user.id), self.class_name,
                                        list(self.submitted_user_keywords_accepted), delta_points, self.img_url)

        await self.user.send(embed=success_embed(
            '''
            Submission submitted.
            You will be notified soon if your submission is accepted.
            
            **ID:** `{}`
            (The acceptance message will contain this ID.)
            '''.format(post.id)
        ))