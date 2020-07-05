import discord
from database import *
from tabulate import tabulate

class Leaderboard:
    def __init__(self, bot: discord.Client, guild_id, leaderboard_channel):
        self.bot = bot
        self.top = {}  # user => points
        self.contest_id = -1
        self.guild_id = guild_id
        self.leaderboard_channel = leaderboard_channel

    def set_contest_id(self, new_contest_id):
        self.contest_id = new_contest_id

    async def update(self):
        self.top = Database.get_top_users(self.contest_id, 100)

    async def display(self):
        if self.top is None:
            return

        place = 0
        table_ind = 0  # limit of 5 tables
        player_count = 0  # limit each table to hold 20 players
        prev_points = float("inf")
        table_list = []

        for i in range(0, 5):
            table_list.append([])
            table_list[i] = []

        guild = self.bot.get_guild(int(self.guild_id))

        sorted_data = []  # (ign, class, points)
        for character in self.top:
            player = guild.get_member(int(character["user_id"]))
            if player is None:
                continue
            ign = player.nick
            sorted_data.append((ign, character["class"], character["points"]))

        sorted_data = sorted(sorted_data, key=lambda tup: tup[2], reverse=True)

        for ign, class_str, points in sorted_data:
            # TODO: make sure all occurrences where you're looking for a player are validated

            if player_count >= 15:  # maxed out players for this table
                table_ind += 1
                player_count = 0
            if table_ind >= 5:  # maxed out tables
                break
            player_count += 1
            if points >= prev_points:  # continue with same place
                table_list[table_ind].append([None, ign, points, class_str])
            else:  # move down a place
                place += 1
                table_list[table_ind].append([place, ign, points, class_str])

        embed = discord.Embed(title="Leaderboard", color=0x00FF00)
        embed.description = "Updated every 10 minutes during a contest."

        for i in range(0, 5):
            if len(table_list[i]) == 0:
                break
            table_str = tabulate(table_list[i], headers=["Rank", "Player", "Points", "Class"])
            embed.add_field(name='\u200b', value="```" + table_str + "```", inline=False)

        ch: discord.TextChannel = discord.utils.get(self.bot.get_guild(int(self.guild_id)).text_channels, name=self.leaderboard_channel)

        def is_me(m):
            return m.author == self.bot.user

        try:
            await ch.purge(limit=100, check=is_me)
        except:
            print("Failed to delete old leaderboard.")

        new_post = await ch.send(embed=embed)
