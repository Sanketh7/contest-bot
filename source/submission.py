import discord
import asyncio
from flashtext import KeywordProcessor
import database as db
from util import error_embed, success_embed

class Submission:
    def __init__(self, bot: discord.Client, user: discord.User, player_reacts: dict,
                 guild_id: str, sub_channel_name: str, keyword_data: dict, points_data: dict, contest_id: int, points_doc: str):

        self.bot = bot
        self.user = user
        self.player_reacts = player_reacts
        self.sub_channel_name = sub_channel_name
        self.guild_id = guild_id
        self.keyword_data = keyword_data
        self.points_data = points_data
        self.contest_id = contest_id
        self.points_doc = points_doc

        self.class_name = ""  # will be resolved in class_select_menu
        self.img_url = ""
        self.user_keywords = set()
        self.points = 0

    async def start_process(self):
        await self.class_select_menu()

    async def timed_out_response(self):
        # await self.user.send("Uh oh! You did not respond in time so the process timed out.")
        await self.user.send(embed=error_embed("Uh oh! You did not respond in time so the process timed out."))

    async def do_player_reacts(self, dm_msg):
        for e in self.player_reacts.values():
            await dm_msg.add_reaction(e)

    async def do_confirm_reacts(self, dm_msg):
        for e in ["✅", "❌"]:
            await dm_msg.add_reaction(e)

    async def class_select_menu(self):
        embed = discord.Embed(title="Class Selection.")
        embed.add_field(
            name="Note",
            value=
            '''
            **This will ERASE previous submissions for this contest, regardless of class.**
            ''',
            inline=False
        )
        embed.add_field(
            name="Instructions",
            value=
            '''
            React to one of the class reactions below to select a class for this contest.
            You should then be given a place to submit your screenshot.
            
            (You have **5 minutes** to complete this.)
            '''
        )
        dm_msg = await self.user.send(embed=embed)
        react_task = asyncio.create_task(self.do_player_reacts(dm_msg=dm_msg))
        await asyncio.sleep(0)

        def check(react_got: discord.Reaction, user_got: discord.User):
            return user_got.id == self.user.id and str(react_got) in self.player_reacts.values()

        try:
            reaction, user2 = await self.bot.wait_for('reaction_add', timeout=(60.0*5), check=check)
        except asyncio.TimeoutError:  # menu timed out
            await react_task
            await self.timed_out_response()
        else:  # successfully got a reaction
            await react_task
            self.class_name = next((name for name, emoji_str in self.player_reacts.items() if emoji_str == str(reaction)), None)
            await self.proof_menu()

    async def proof_menu(self):
        embed = discord.Embed(title="Submission for class `" + self.class_name + "`.")
        embed.add_field(
            name="Instructions",
            value=
            '''
            Send a message with a screenshot **in this DM** as specified in the contest rules. 
            Click the **plus button** next to where you type a message to attach an image \
            or **copy and paste** and image into the message box.
            If you do not use either of the methods above, the bot **cannot** detect it.
            
            **You MUST have the following things present in your screenshot:**
            - username
            - equipped items + inventory
            - player stats (i.e. defense, wisdom, etc)
            - fame gained
            
            **If you do not include all these items, your submission may be denied.**
            
            (You have **15 minutes** to complete this.)
            ''',
            inline=False
        )
        dm_msg = await self.user.send(embed=embed)

        def check(m: discord.Message):
            return len(m.attachments) > 0 and m.attachments[0].url is not None

        try:
            res = await self.bot.wait_for('message', timeout=(60.0*15), check=check)
        except asyncio.TimeoutError:  # timed out
            await self.timed_out_response()
        else:  # got an image
            # ch = discord.utils.get(self.bot.get_guild(int(self.guild_id)).text_channels, name=self.sub_channel_name)
            # await ch.send(res.attachments[0].url)
            self.img_url = res.attachments[0].url
            await self.keyword_menu()

    async def keyword_menu(self):
        embed = discord.Embed(title="Keywords Entry")
        embed.add_field(
            name="Instructions",
            value=
            '''
            Using this [document]({}) as reference, enter the keywords that correspond to your items/achievements.
            This is how you will get your points.
            
            **If points are not entered correctly, your submission will be denied.**
            
            (You have **15 minutes** to complete this.)
            '''.format(self.points_doc)
        )
        dm_msg = await self.user.send(embed=embed)

        def check(m: discord.Message):
            return len(m.content) > 0 and m.guild is None

        try:
            res = await self.bot.wait_for('message', timeout=(60.0*15), check=check)
        except asyncio.TimeoutError:
            await self.timed_out_response()
        else:
            self.parse_keywords(res.content)
            await self.confirm_keywords_menu()

    def parse_keywords(self, data):
        proc = KeywordProcessor()
        proc.add_keywords_from_dict(self.keyword_data)
        items = proc.extract_keywords(data)

        self.points = 0
        self.user_keywords = set()

        for item in items:
            self.user_keywords.add(item)

        for item in self.user_keywords:
            self.points += self.points_data[item][self.class_name]

    async def confirm_keywords_menu(self):
        item_str = ""
        if len(self.user_keywords) > 0:
            item_str = str(self.user_keywords)
        else:
            item_str = "**NONE**"
        embed = discord.Embed(title="Confirm Keywords")
        embed.add_field(
            name="Found Keywords:",
            value="`" + item_str + "`"
            + "\n\nReact with ✅ if these are correct, ❌ to type in keywords again."
            + "\n(You have **5 minutes** to complete this.)"
        )

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
                await self.keyword_menu()
                return
            await self.confirm_menu()

    async def confirm_menu(self):
        embed = discord.Embed(title="Confirm Submission")
        embed.description = \
        '''
        ✅ - Confirm submission (**overwrites** previous submissions)
        ❌ - Cancel submission
        
        If you do NOT get a message after this, that means your submission **failed**.
        
        (You have **5 minutes** to complete this.)
        '''
        dm_msg = await self.user.send(embed=embed)

        valid_reactions = ['✅', '❌']

        react_task = asyncio.create_task(self.do_confirm_reacts(dm_msg=dm_msg))
        await asyncio.sleep(0)

        def check(react_got: discord.Reaction, user_got: discord.User):
            return user_got.id == self.user.id and str(react_got) in valid_reactions

        try:
            reaction, user2 = await self.bot.wait_for('reaction_add', timeout=(60.0*5), check=check)
        except asyncio.TimeoutError:
            await react_task
            await self.timed_out_response()
        else:
            await react_task
            if str(reaction) == "❌":
                # await self.user.send("You cancelled the submission.")
                return await self.user.send(embed=success_embed("Submission cancelled."))
            await self.upload_submission()

    async def upload_submission(self):
        member: discord.Member = discord.utils.get(self.bot.get_guild(int(self.guild_id)).members, id=self.user.id)
        if member is None:
            return
        embed = discord.Embed(title=member.display_name + "    (" + str(self.class_name) + ")")
        embed.add_field(name="Items/Achievements", value="`"+str(self.user_keywords)+"`", inline=False)
        embed.add_field(name="Points", value=("**" + str(self.points) + "**"))
        embed.set_image(url=self.img_url)

        ch: discord.TextChannel = discord.utils.get(self.bot.get_guild(int(self.guild_id)).text_channels, name=self.sub_channel_name)
        post = await ch.send(embed=embed)
        await post.add_reaction("✅")
        await post.add_reaction("❌")

        prev_post = await db.add_submission_to_user(self.contest_id, self.user.id, post.id, {
            "class": self.class_name,
            "keywords": list(self.user_keywords),
            "points": self.points,
            "img_url": self.img_url
        })

        cnt = await db.add_submission_count(self.contest_id, self.user.id)

        # await self.user.send("Submission was successful!")
        await self.user.send(embed=success_embed(
            '''
            Submission submitted.
            You will be notified soon if your submission is accepted.
            
            You have **{}** submission attempts left.
            
            **ID:** `{}`
            (The acceptance message will contain this ID.)
            '''.format(str(cnt), post.id)
        ))

        # Now delete the previous submission verification post if it exists
        if prev_post is None:
            return

        try:
            msg = await ch.fetch_message(int(prev_post))
            await msg.delete()
        except:
            print("Couldn't delete previous verification post. This could be because it was deleted normally.")