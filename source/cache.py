from source.database.database import DB
import discord


class Cache:
    contest_id: int
    contest_post_id: int
    contest_end_time: float
    is_contest_active: bool
    contest_points_document_url: str
    guild: discord.Guild
    leaderboard_channel: discord.TextChannel

    @staticmethod
    def reload():
        DB.update_cache()
        # TODO load guild from ENV and load leaderboard channel
