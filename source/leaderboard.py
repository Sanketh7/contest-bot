import discord
from database.database import *
from tabulate import tabulate
from cache import Cache


class Leaderboard:
    bot: discord.Client
    top: list  # list of character payloads

    @staticmethod
    def init(bot: discord.Client):
        Leaderboard.bot = bot

    @staticmethod
    async def update():
        Leaderboard.top = DB.get_top_characters(100)

    async def display():
        if Leaderboard.top is None:
            return

        place = 0
        table_ind = 0  # limit of 5 tables
        player_count = 0  # limit each table to hold 10 players
        prev_points = float("inf")
        table_list = []

        for i in range(0, 5):
            table_list.append([])
            table_list[i] = []

        guild = Cache.guild

        sorted_data = []  # (ign, class, points, is_active)
        for character in Leaderboard.top:
            player = guild.get_member(character.user_id)
            if player is None:
                continue
            ign = player.display_name
            sorted_data.append((ign, character.rotmg_class, character.points, character.is_active))

        sorted_data = sorted(sorted_data, key=lambda tup: tup[2], reverse=True)

        for ign, class_str, points, is_active in sorted_data:
            # TODO: make sure all occurrences where you're looking for a player are validated

            if player_count >= 10:  # maxed out players for this table
                table_ind += 1
                player_count = 0
            if table_ind >= 5:  # maxed out tables
                break
            player_count += 1
            if points >= prev_points:  # continue with same place
                table_list[table_ind].append([None, ign, points, class_str, "✅" if bool(is_active) else " "])
            else:  # move down a place
                place += 1
                table_list[table_ind].append([place, ign, points, class_str, "✅" if bool(is_active) else " "])

        embed = discord.Embed(title="Leaderboard", color=0x00FF00)
        embed.description = "Updated every 10 minutes during a contest."

        for i in range(0, 5):
            if len(table_list[i]) == 0:
                break
            table_str = tabulate(table_list[i], headers=["Rank", "Player", "Points", "Class", "Active?"])
            embed.add_field(name='\u200b', value="```" + table_str + "```", inline=False)

        def is_me(m):
            return m.author == self.bot.user

        try:
            await Cache.leaderboard_channel.purge(limit=100, check=is_me)
        except:
            print("Failed to delete old leaderboard.")

        new_post = await Cache.leaderboard_channel.send(embed=embed)
