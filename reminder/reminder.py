import datetime
import os
from typing import Optional

import asyncio
import parsedatetime as pdt
import requests

import discord
from discord.ext import commands


WIT_API_KEY = os.getenv("WIT_API_KEY", "")


class ReminderCron:

    def __init__(self, cancel_message: int, initial_message: int, author: int, channel: int, dt: Optional[float]):
        if dt is None:
            tmp = datetime.datetime.now() + datetime.timedelta(days=1)
            dt = tmp.timestamp()
        self.dt: float = dt
        self.cancel_message = cancel_message
        self.initial_message = initial_message
        self.author = author
        self.channel = channel


class Reminder(commands.Cog):
    """Reminder Plugin"""

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.reminders: list[ReminderCron] = []
        self.cal = pdt.Calendar()


    async def send_reminder(self, rmc: ReminderCron):
        try:
            print("Preparing to send...")
            if rmc in self.reminders:
                print("Found in the list!")
                ch = self.bot.get_channel(rmc.channel)
                print("Channel: ", ch.name)
                msg = await ch.fetch_message(rmc.initial_message)
                print("Message: ", msg.content[:20], "...")

                await msg.reply("Reminding you to do this!! <:yello:1147137527896092703>", mention_author=True)
                self.reminders.remove(rmc)
                print("Replied")
        except Exception as e:
            print(e)


    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        if not reaction.is_custom_emoji() and reaction.emoji == "❌":
            rmc = discord.utils.get(self.reminders, cancel_message=reaction.message.id)
            if rmc is not None and rmc.author == user.id:
                self.reminders.remove(rmc)
                await reaction.message.delete()


    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        r = requests.get(
            f"https://api.wit.ai/message?v=20240705&q={message.content[:280]}",
            headers={
                "Authorization": f"Bearer {WIT_API_KEY}"
            }
        )

        j = r.json()
        if len(j["intents"]) and j["intents"][0]["name"] == "Reminder":
            print("Reminder detected")

            dtt = "tomorrow"
            if "wit$datetime:datetime" in j["entities"].keys():
                dtt = j["entities"]["wit$datetime:datetime"][0]["body"]

            dt: datetime.datetime = self.cal.parseDT(dtt, datetime.datetime.now())[0]

            msg = await message.reply(
                f"Reminder set on <t:{int(dt.timestamp())}:f> <:RuanMeiNote:1227533354178580510>",
                mention_author=False
            )
            await msg.add_reaction("❌")

            rmc = ReminderCron(
                cancel_message=msg.id,
                initial_message=message.id,
                author=message.author.id,
                channel=message.channel.id,
                dt=dt.timestamp()
            )
            self.reminders.append(rmc)

            print("Scheduling...")
            self.bot.loop.call_at(dt.timestamp(), asyncio.create_task, self.send_reminder(rmc))
            self.bot.loop.call_at(dt.timestamp(), print, "Should trigger now")
            print("Scheduled...")


async def setup(bot: commands.Bot):
    await bot.add_cog(Reminder(bot))
