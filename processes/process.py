import discord
from util import error_embed, success_embed


class Process:
    def __init__(self, bot: discord.Client, user: discord.User, contest_id: int):
        self.bot = bot
        self.user = user
        self.contest_id = contest_id
        self.dead = False # True if the process is finished

    # used if the user didn't respond to an embed prompt in time
    async def timed_out(self):
        return await self.user.send(embed=error_embed("Uh oh! You did not respond in time so the process timed out."))

    # used if the user cancelled the process
    async def cancelled(self):
        self.dead = True
        return await self.user.send(embed=success_embed("Cancelled."))

    # used if the user finished the process
    # note that this is intended to be an abstract method
    async def finished(self):
        self.dead = True
        raise NotImplementedError()

    # used if the user started the process
    # note that this is intended to be an abstract method
    async def start(self):
        raise NotImplementedError()
