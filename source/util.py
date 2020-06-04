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
    async def send_log(text: str):
        ch: discord.TextChannel = discord.utils.get(Logger.bot.get_guild(int(Logger.guild_id)).text_channels,
                                                    name=Logger.log_channel_name)
        embed = discord.Embed(color=0x0000FF)
        embed.description = text

        await ch.send(embed=embed)

    @staticmethod
    async def accepted_submission(staff_user_id: int, player_user_id: int, pending_submission_data: object):
        # pending_submission_data is the data that was stored in contests/pending/{post_id}/

        try:
            staff_user = Logger.bot.get_user(staff_user_id)
            player_user = Logger.bot.get_user(player_user_id)
        except:
            return

        if "keywords" in pending_submission_data:
            if len(pending_submission_data["keywords"]) > 0:
                item_str = str(pending_submission_data)
            else:
                item_str = "**NONE**"
        else:
            item_str = "**NONE**"

        text = '''
        {} accepted {}'s submission:
        Class: {}
        Items/Achievements: `{}`
        Points: {}
        '''.format(staff_user.mention, player_user.mention, pending_submission_data["class"],
                   item_str, pending_submission_data["points"])

        await Logger.send_log(text)

    @staticmethod
    async def force_update_leaderboard(user: discord.User):
        text = '''
        {} forcibly updated the leaderboard.
        '''.format(user.mention)
        await Logger.send_log(text)
