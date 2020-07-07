import discord


def error_embed(text: str):
    embed = discord.Embed(color=0xFF0000)
    embed.description = "❌ " + text
    return embed


def success_embed(text: str):
    embed = discord.Embed(color=0x00FF00)
    embed.description = "✅ " + text
    return embed

class Logger:
    bot: discord.Client
    guild_id: str
    log_channel_name: str

    @staticmethod
    def init(bot: discord.Client, guild_id: str, log_channel: str):
        Logger.bot = bot
        Logger.guild_id = guild_id
        Logger.log_channel_name = log_channel

    @staticmethod
    async def send_log(text: str, embed_color, image_url = None):
        ch: discord.TextChannel = discord.utils.get(Logger.bot.get_guild(int(Logger.guild_id)).text_channels,
                                                    name=Logger.log_channel_name)
        embed = discord.Embed(color=embed_color)
        embed.description = text

        if image_url != None:
            embed.set_image(url=image_url)

        await ch.send(embed=embed)

    @staticmethod
    async def accepted_submission(staff_user_id: int, player_user_id: int, pending_submission_data):
        # pending_submission_data is the data that was stored in contests/pending/{post_id}/

        try:
            staff_user = Logger.bot.get_user(staff_user_id)
            player_user = Logger.bot.get_user(player_user_id)
        except:
            return

        if "keywords" not in pending_submission_data:
            pending_submission_data["keywords"] = set()

        if len(pending_submission_data["keywords"]) > 0:
            item_str = str(pending_submission_data["keywords"])
        else:
            item_str = "**NONE**"

        text = '''
        {} accepted {}'s submission:
        Class: {}
        Items/Achievements: `{}`
        Points: {}
        Proof: [image]({})
        '''.format(staff_user.mention, player_user.mention, pending_submission_data["class"],
                   item_str, pending_submission_data["points"], pending_submission_data["img_url"])

        await Logger.send_log(text, 0x00FF00, pending_submission_data["img_url"])

    @staticmethod
    async def rejected_submission(staff_user_id: int, player_user_id: int, pending_submission_data):
        # pending_submission_data is the data that was stored in contests/pending/{post_id}/

        try:
            staff_user = Logger.bot.get_user(staff_user_id)
            player_user = Logger.bot.get_user(player_user_id)
        except:
            return

        if "keywords" not in pending_submission_data:
            pending_submission_data["keywords"] = set()

        if len(pending_submission_data["keywords"]) > 0:
            item_str = str(pending_submission_data["keywords"])
        else:
            item_str = "**NONE**"

        text = '''
        {} rejected {}'s submission:
        Class: {}
        Items/Achievements: `{}`
        Points: {}
        Proof: [image]({})
        '''.format(staff_user.mention, player_user.mention, pending_submission_data["class"],
                   item_str, pending_submission_data["points"], pending_submission_data["img_url"])

        await Logger.send_log(text, 0xFF0000, pending_submission_data["img_url"])

    @staticmethod
    async def force_update_leaderboard(user: discord.User):
        text = '''
        {} forcibly updated the leaderboard.
        '''.format(user.mention)
        await Logger.send_log(text, 0x0000FF)

    @staticmethod
    async def removed_items(staff_user_id, player_user_id, char_id, items_removed):
        try:
            staff_user = Logger.bot.get_user(staff_user_id)
            player_user = Logger.bot.get_user(player_user_id)
        except:
            return

        text = '''
        {} removed these keywords from {}'s character (ID: `{}`):
        `{}`
        '''.format(staff_user.mention, player_user.mention, char_id, items_removed)

        await Logger.send_log(text, 0xFF0000)

    @staticmethod
    async def added_items(staff_user_id, player_user_id, char_id, items_added):
        try:
            staff_user = Logger.bot.get_user(staff_user_id)
            player_user = Logger.bot.get_user(player_user_id)
        except:
            return

        text = '''
        {} added these keywords to {}'s character (ID: `{}`):
        `{}`
        '''.format(staff_user.mention, player_user.mention, char_id, items_added)

        await Logger.send_log(text, 0x00FF00)
