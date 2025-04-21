import discord
from discord.ext import commands


class MessageCounter:

    def __init__(self):
        self.message = None
        self.count = 0
        self.users = []
        self.stickers = None


class Parrot(commands.Cog):
    """Funpost Plugin"""

    def __init__(self, bot):
        self.bot = bot
        self.messages: dict[int, MessageCounter] = {}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if message.channel.id not in self.messages:
            self.messages[message.channel.id] = MessageCounter()

        ct = self.messages[message.channel.id]
        if message.content == ct.message or (message.stickers and ct.stickers and message.stickers[0].id == ct.stickers[0].id):
            if message.author.id not in ct.users:
                ct.count += 1
                ct.users.append(message.author.id)
        else:
            if message.content:
                ct.message = message.content
            else:
                ct.message = None
            ct.users = [message.author.id]
            ct.count = 1
            ct.stickers = message.stickers

        if ct.count == 4:
            await message.channel.send(content=ct.message, stickers=ct.stickers)
            ct.count += 1


async def setup(bot):
    await bot.add_cog(Parrot(bot))

