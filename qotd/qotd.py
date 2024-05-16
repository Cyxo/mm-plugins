import json
import os
import random
import uuid
from datetime import datetime

import aiocron
import discord
from discord.ext import commands

from core import checks
from core.paginator import EmbedPaginatorSession
from core.models import PermissionLevel


QUESTIONS_FILE = os.path.dirname(__file__) + "/qotd.json"

QOTD_STICKERS = [
    "https://media.discordapp.net/attachments/1106785083379171372/1157133462331985961/20230928_174023.png?ex=65178003&is=65162e83&hm=dc1d01d630f54b13f7bea3dc29be717a279dd46929041dd34745880963379621&",
    "https://media.discordapp.net/attachments/1106785083379171372/1156858924838965268/Untitled570_20230928144333.png?ex=65168055&is=65152ed5&hm=257aeb2eb1d4596009f0ef092adf2e8573242cfae51116e0685545bfa322b87d&=&width=703&height=655",
    "https://media.discordapp.net/attachments/1106793246748848199/1156482829098692649/20230926_233455.png?ex=65152210&is=6513d090&hm=0a5126e8622729f3baa2b31b69dcfef12c9e4d0808e9c09ab9febb46692489bb&=&width=655&height=655",
    "https://media.discordapp.net/attachments/1106793246748848199/1156482828868014100/20230926_230548.png?ex=65152210&is=6513d090&hm=3d90ac3e06e7c44fbb399bf9d06a7634d88940a51d533e086c44cb21c6775077&=&width=334&height=333",
    "https://media.discordapp.net/attachments/1106785083379171372/1156341810042515486/20230926_013519.png?ex=65149ebb&is=65134d3b&hm=330623a1c4b273c609e548740ca66145e5d0365735b3bfbf76348454492b6e4a&=&width=655&height=655",
    "https://media.discordapp.net/attachments/1106785083379171372/1156341810315149395/20230926_013109.png?ex=65149ebb&is=65134d3b&hm=b30994a003ffd066581127220f869c6d90ad41810e86034e0117df45a4748500&=&width=655&height=655",
    "https://media.discordapp.net/attachments/1106785083379171372/1156341810868793505/20230926_002553.png?ex=65149ebb&is=65134d3b&hm=71997888a7a9399fc9443d2b454c55aaa409d95b8bfeb9c83f90017265284d64&=&width=655&height=655",
    "https://cdn.discordapp.com/attachments/1117346551644295239/1158876241093464264/ruan_mei_nerd.png?ex=651dd71a&is=651c859a&hm=06c83048f9ec6c405cd1c5ebf169214cf4db9b9e655d6711854ee1003febd15d&",
    "https://cdn.discordapp.com/attachments/1117346551644295239/1158876240736956526/ruanmeifingerheart.png?ex=651dd71a&is=651c859a&hm=0a506f0784a73f21d142dfa4dcf747854a1b00fdaa378d2db70a6359fb074b15&",
    "https://cdn.discordapp.com/attachments/1117346551644295239/1158876415614255194/ruanmei_bugcat_nod.gif?ex=651dd744&is=651c85c4&hm=c7e78157961d9421ec7d9445b6c23d3c16832b732673e5b51fded27929691949&",
    "https://cdn.discordapp.com/attachments/1117346551644295239/1158876605804986389/ruanmeijoy1.png?ex=651dd771&is=651c85f1&hm=d2b89fc3e7b7b5a426a67b6c54e30d357db69e1e0ee98fe47359e79e3935c33a&",
    "https://cdn.discordapp.com/attachments/1117346551644295239/1158876917269803088/20230926_230006.png?ex=651dd7bb&is=651c863b&hm=8768cd09a5fd98b9105293645c12a6f1e121e0ae9e9e0223108537ee8bda8806&",
    "https://cdn.discordapp.com/attachments/1117346551644295239/1158876917609537556/ruan_mei_eyebrow_raise.png?ex=651dd7bc&is=651c863c&hm=29ad9b9f9bd18ca6cba98f5b79ed564ef489f9beefe8764d94b2b3206188e23b&",
    "https://cdn.discordapp.com/attachments/1117346551644295239/1158876917836042290/20230926_012018.gif?ex=651dd7bc&is=651c863c&hm=9bbace8884217e3c582c89d5e5f61496baced80d0c462790f82bbb64c65d2d95&",
    "https://cdn.discordapp.com/attachments/1117346551644295239/1158877082860912661/ruanmeidead.png?ex=651dd7e3&is=651c8663&hm=3690617f2abd9143677c348a9c947d1cc6f0d4b1393296fac131c4df86e5e14d&",
    "https://cdn.discordapp.com/attachments/1117346551644295239/1158877083657846824/ruanpackwatch.png?ex=651dd7e3&is=651c8663&hm=876634884d7a439207bafbc26916a03f6b1c1b68d029a94b57168463ddda3208&",
    "https://cdn.discordapp.com/emojis/1153489300051202198.png",
    "https://cdn.discordapp.com/emojis/1155737942506078278.png",
    "https://cdn.discordapp.com/emojis/1155740644040519690.png",
    "https://media.discordapp.net/attachments/1135997360695152690/1160583122589589674/ruan_mei_bugcat_flower_raw.gif",
]

QOTD_REACT_EMOTES = [
    1160566321306673233,
    1160588883516473464,
    1153489300051202198,
    1156319608630935584,
    1154897211235258390,
    1157943933683384382,
    1154671375970209852,
    1155737942506078278,
    1147153985275437056,
    1157946531773681704,
    1165960500681650196,
    1164689665740259369,
    1152230094312591360,
    1165171669862727771,
    1157946537737977896,
    1157946544000082021,
    1162001731266297917,
    1156150407228309564,
    1153463866160848936,
    1162240804467785808
]

COG_NAME = "QOTD"


class QOTDs(commands.Cog, name=COG_NAME):
    """Manages questions of the day and sends them periodically."""


    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cog_id = uuid.uuid4()

        if os.path.exists(QUESTIONS_FILE):
            self.load_conf()
        else:
            self.conf = {
                "questions": [],
                "time": "0 8 * * *",
                "channel": None,
                "react_channel": None,
                "ping_role": None,
                "admin_channel": None,
                "admin_role": None,
                "warning_threshold": 2
            }

        self.questions: list = self.conf["questions"]
        self.time: str = self.conf["time"]
        self.channel_id: int = self.conf["channel"]
        self.react_channel_id: int = self.conf["react_channel"]
        self.ping_role_id: int = self.conf["ping_role"]
        self.admin_channel_id: int = self.conf["admin_channel"]
        self.admin_role_id: int = self.conf["admin_role"]
        self.warning_threshold: int = self.conf["warning_threshold"]

        self.cron = aiocron.crontab(self.time, func=self.send_question)

        self.footer = ""  # TODO: added just in case we do something with it someday


    def load_conf(self):
        with open(QUESTIONS_FILE, "r") as f:
            self.conf = json.load(f)

        if "questions" not in self.conf:
            self.conf["questions"] = []
        else:
            bad_idx = []
            for idx, question in enumerate(self.conf["questions"]):
                if not isinstance(question, dict) \
                            or "title" not in question.keys() \
                            or "options" not in question.keys() \
                            or not isinstance(question["options"], list):
                    bad_idx.append(idx)

            for idx in bad_idx:
                self.conf["questions"].pop(idx)

        if "time" not in self.conf:
            self.conf["time"] = "0 8 * * *"

        if "channel" not in self.conf:
            self.conf["channel"] = None

        if "react_channel" not in self.conf:
            self.conf["react_channel"] = None

        if "ping_role" not in self.conf:
            self.conf["ping_role"] = None

        if "admin_channel" not in self.conf:
            self.conf["admin_channel"] = None

        if "admin_role" not in self.conf:
            self.conf["admin_role"] = None

        if "warning_threshold" not in self.conf:
            self.conf["warning_threshold"] = 2


    def save_conf(self):
        self.conf = {
            "questions": self.questions,
            "time": self.time,
            "channel": self.channel_id,
            "react_channel": self.react_channel_id,
            "ping_role": self.ping_role_id,
            "admin_channel": self.admin_channel_id,
            "admin_role": self.admin_role_id,
            "warning_threshold": self.warning_threshold
        }

        with open(QUESTIONS_FILE, "w+") as f:
            json.dump(self.conf, f)


    async def warn_admins(self, message: str):
        if self.admin_channel_id is not None:
            channel: discord.TextChannel = self.bot.get_channel(self.admin_channel_id)

            if channel is None:
                return

            role = None
            if self.admin_role_id is not None:
                role = channel.guild.get_role(self.admin_role_id).mention
            if role is None:
                role = ""

            embed = discord.Embed(
                title="Admin warning",
                description=f"{message}".strip(),
                colour=discord.Colour.red()
            )
            embed.set_footer(text=self.footer)

            await channel.send(content=role, embed=embed)


    def make_question(self, question, guild):
        react_channel = None
        if self.react_channel_id is not None:
            react_channel: discord.TextChannel = self.bot.get_channel(self.react_channel_id)

        reactions = random.sample(QOTD_REACT_EMOTES, len(question["options"]))
        react_emotes = []
        description = []
        for index, option in enumerate(question["options"]):
            emote = discord.utils.get(guild.emojis, id=reactions[index])
            react_emotes.append(emote)
            description.append(f"{emote} {option}")

        if react_channel is not None:
            description.append(f"*You can discuss in {react_channel.mention}*")

        embed = discord.Embed(
            title=question["title"],
            description="\n\n".join(description),
            colour=discord.Colour.random()
        )
        embed.set_thumbnail(url=random.choice(QOTD_STICKERS))
        embed.set_footer(text=self.footer)

        return react_emotes, embed


    async def send_question(self):
        cog: QOTDs = self.bot.get_cog(COG_NAME)
        if cog is None or cog.cog_id != self.cog_id:
            # We are in an old cog after update and don't have to send QOTD anymore
            self.cron.stop()
            return

        if self.channel_id is not None:
            channel: discord.TextChannel = self.bot.get_channel(self.channel_id)

            if channel is None:
                await self.warn_admins("QOTD channel does not exist (anymore)")
                return

            if len(self.questions) == 0:
                await self.warn_admins("No questions to send today :frowning:")
                return


            question = self.questions.pop(0)
            self.save_conf()
            react_emotes, embed = self.make_question(question, channel.guild)

            content = ""
            if self.ping_role_id is not None:
                content = channel.guild.get_role(self.ping_role_id).mention

            message = await channel.send(content=content, embed=embed)

            if len(self.questions) <= self.warning_threshold:
                await self.warn_admins(f"Only {len(self.questions)} upcoming questions left!")

            for emote in react_emotes:
                await message.add_reaction(emote)
        else:
            await self.warn_admins("QOTD channel was not set!")


    @commands.group(invoke_without_command=True)
    @commands.has_role("QOTD Manager")
    async def qotd(self, ctx):
        """
        Manage Questions of the Day.
        """

        await ctx.send_help(ctx.command)


    # Add question of the day
    @commands.has_role("QOTD Manager")
    @qotd.command(name="add", aliases=["create"])
    async def add_qotd(self, ctx: commands.Context, title: str, *options: str):
        """Adds a question of the day and saves it"""

        if len(options) <= len(QOTD_REACT_EMOTES):
            question = {
                "title": title,
                "options": list(options)
            }

            self.questions.append(question)
            self.save_conf()

            description = f'Question "{title}" added '
            emote = discord.utils.get(ctx.guild.emojis, id=1160566321306673233)
            colour = discord.Colour.dark_green()
        else:
            description = f"Max {len(QOTD_REACT_EMOTES)} options! "
            emote = discord.utils.get(ctx.guild.emojis, id=1160588883516473464)
            colour = discord.Colour.red()

        embed = discord.Embed(
            title="New question",
            description=f"{description}{emote}",
            colour=colour
        )
        embed.set_footer(text=self.footer)

        await ctx.send(embed=embed)


    # List questions of the day
    @commands.has_role("QOTD Manager")
    @qotd.command(name="list")
    async def list_qotd(self, ctx: commands.Context):
        """Lists upcoming questions of the day"""

        embeds = []
        description = ""
        for index, question in enumerate(self.questions):
            description += str(index + 1) + ". "
            description += question["title"]
            description += "\n"

            if index % 5 == 4 or index == len(self.questions) - 1:
                embed = discord.Embed(
                    title="Upcoming questions of the day",
                    description=description.strip(),
                    colour=discord.Colour.dark_green()
                )
                embed.set_footer(text=self.footer)
                embeds.append(embed)
                description = ""
        
        if len(embeds) == 0:
            description = "*No upcoming questions* :frowning:"
            embed = discord.Embed(
                title="Upcoming questions of the day",
                description=description.strip(),
                colour=discord.Colour.dark_green()
            )
            embed.set_footer(text=self.footer)
            await ctx.send(embed=embed)
        else:
            paginator = EmbedPaginatorSession(ctx, *embeds)
            await paginator.run()


    # Remove a question of the day
    @commands.has_role("QOTD Manager")
    @qotd.command(name="remove", aliases=['delete', 'del', 'rm'])
    async def remove_qotd(self, ctx: commands.Context, number: int):
        """Removes a question (use `?qotd list` to find the number)"""

        if number > 0 and number <= len(self.questions):
            idx = number - 1
            question = self.questions.pop(idx)
            self.save_conf()

            description = f'Question "{question["title"]}" removed '
            emote = discord.utils.get(ctx.guild.emojis, id=1153489300051202198)
            colour = discord.Colour.dark_green()
        else:
            description = f"Question number {number} doesn't exist "
            emote = discord.utils.get(ctx.guild.emojis, id=1156319608630935584)
            colour = discord.Colour.red()

        embed = discord.Embed(
            title="Remove question",
            description=f"{description}{emote}",
            colour=colour
        )
        embed.set_footer(text=self.footer)

        await ctx.send(embed=embed)


    # Edit question of the day
    @commands.has_role("QOTD Manager")
    @qotd.command(name="edit")
    async def edit_qotd(self, ctx: commands.Context, number: int, title: str = None, *options: str):
        """Edits a question. Use `?qotd edit number` to show the command used to create the question."""

        if number > 0 and number <= len(self.questions):
            idx = number - 1

            if title is not None:
                if len(options) <= len(QOTD_REACT_EMOTES):
                    question = {
                        "title": title,
                        "options": list(options)
                    }

                    self.questions[idx] = question
                    self.save_conf()

                    description = f'Question "{question["title"]}" edited '
                    emote = discord.utils.get(ctx.guild.emojis, id=1153489300051202198)
                    colour = discord.Colour.dark_green()
                else:
                    description = f"Max {len(QOTD_REACT_EMOTES)} options! "
                    emote = discord.utils.get(ctx.guild.emojis, id=1160588883516473464)
                    colour = discord.Colour.red()
            else:
                question = self.questions[idx]

                description = f"Here is the command used:\n\n```?qotd edit {number} \"{question['title']}\" {' '.join([chr(34) + option + chr(34) for option in question['options']])}```"
                emote = ""
                colour = discord.Colour.dark_green()
        else:
            description = f"Question number {number} doesn't exist "
            emote = discord.utils.get(ctx.guild.emojis, id=1156319608630935584)
            colour = discord.Colour.red()

        embed = discord.Embed(
            title="Edit question",
            description=f"{description}{emote}",
            colour=colour
        )
        embed.set_footer(text=self.footer)

        await ctx.send(embed=embed)


    # Move a question of the day
    @commands.has_role("QOTD Manager")
    @qotd.command(name="move")
    async def move_qotd(self, ctx: commands.Context, number: int, position: int):
        """Moves a question to the specified position"""

        if number > 0 and number <= len(self.questions):
            if position > 0 and position <= len(self.questions):
                idx = number - 1
                new_idx = position - 1
                question = self.questions.pop(idx)
                self.questions.insert(new_idx, question)
                self.save_conf()

                description = f'Question "{question["title"]}" moved to position {position} '
                emote = discord.utils.get(ctx.guild.emojis, id=1153489300051202198)
                colour = discord.Colour.dark_green()
            else:
                description = f"{position} is not a valid position "
                emote = discord.utils.get(ctx.guild.emojis, id=1156319608630935584)
                colour = discord.Colour.red()
        else:
            description = f"Question number {number} doesn't exist "
            emote = discord.utils.get(ctx.guild.emojis, id=1156319608630935584)
            colour = discord.Colour.red()

        embed = discord.Embed(
            title="Remove question",
            description=f"{description}{emote}",
            colour=colour
        )
        embed.set_footer(text=self.footer)

        await ctx.send(embed=embed)


    # Set the schedule for qotd
    @commands.has_role("QOTD Manager")
    @qotd.command(name="set_time", aliases=['set_schedule'])
    async def set_qotd_time(self, ctx: commands.Context, *, cron: str):
        """Sets the cron time to send the question"""

        if aiocron.croniter.is_valid(cron):
            self.time = cron
            self.save_conf()

            self.cron.stop()
            self.cron = aiocron.crontab(self.time, func=self.send_question)

            base = datetime.now()
            iter = aiocron.croniter(self.time, base)
            ts = int(iter.get_next(datetime).timestamp())
            description = f'Questions scheduled to `{cron}`! Next question will be sent on <t:{ts}:f> '
            emote = discord.utils.get(ctx.guild.emojis, id=1154897211235258390)
            colour = discord.Colour.dark_green()
        else:
            description = f"`{cron}` is an invalid cron format. You may want to check [Crontab Guru](https://crontab.guru/) "
            emote = discord.utils.get(ctx.guild.emojis, id=1157943933683384382)
            colour = discord.Colour.red()

        embed = discord.Embed(
            title="Update questions schedule",
            description=f"{description}{emote}",
            colour=colour
        )
        embed.set_footer(text=self.footer)

        await ctx.send(embed=embed)


    # Set the channel for qotd
    @commands.has_role("QOTD Manager")
    @qotd.command(name="set_channel")
    async def set_qotd_channel(self, ctx: commands.Context, channel: commands.TextChannelConverter = None):
        """Sets the channel to send the questions to (here if none specified)"""

        if channel is None:
            channel = ctx.channel

        self.channel_id = channel.id
        self.save_conf()

        description = f'Questions will be sent in {channel.mention}! '
        emote = discord.utils.get(ctx.guild.emojis, id=1154671375970209852)

        embed = discord.Embed(
            title="Update channel",
            description=f"{description}{emote}",
            colour=discord.Colour.dark_green()
        )
        embed.set_footer(text=self.footer)

        await ctx.send(embed=embed)


    # Set the channel for qotd admin info
    @commands.has_role("QOTD Manager")
    @qotd.command(name="set_react_channel")
    async def set_qotd_react_channel(self, ctx: commands.Context, channel: commands.TextChannelConverter = None):
        """Sets the channel to where people can discuss (here if none specified)"""

        if channel is None:
            channel = ctx.channel

        self.react_channel_id = channel.id
        self.save_conf()

        description = f'People will be told to discuss in {channel.mention}! '
        emote = discord.utils.get(ctx.guild.emojis, id=1155737942506078278)

        embed = discord.Embed(
            title="Update react channel",
            description=f"{description}{emote}",
            colour=discord.Colour.dark_green()
        )
        embed.set_footer(text=self.footer)

        await ctx.send(embed=embed)


    # Set the role to mention for qotd
    @commands.has_role("QOTD Manager")
    @qotd.command(name="set_ping_role")
    async def set_qotd_ping_role(self, ctx: commands.Context, role: commands.RoleConverter = None):
        """Sets the role to ping for QOTD (disable it if none specified)"""

        emote = discord.utils.get(ctx.guild.emojis, id=1147153985275437056)

        if role is not None:
            self.ping_role_id = role.id
            description = f'Will ping {role.mention} for QOTD '
        else:
            self.ping_role_id = None
            description = f'No role will be pinged for QOTD '

        self.save_conf()

        embed = discord.Embed(
            title="Update ping role",
            description=f"{description}{emote}",
            colour=discord.Colour.dark_green()
        )
        embed.set_footer(text=self.footer)

        await ctx.send(embed=embed)


    # Set the channel for qotd admin info
    @commands.has_role("QOTD Manager")
    @qotd.command(name="set_admin_channel")
    async def set_qotd_admin_channel(self, ctx: commands.Context, channel: commands.TextChannelConverter = None):
        """Sets the channel to send admin info to (here if none specified)"""

        if channel is None:
            channel = ctx.channel

        self.admin_channel_id = channel.id
        self.save_conf()

        description = f'Admin info will be sent in {channel.mention}! '
        emote = discord.utils.get(ctx.guild.emojis, id=1155737942506078278)

        embed = discord.Embed(
            title="Update admin channel",
            description=f"{description}{emote}",
            colour=discord.Colour.dark_green()
        )
        embed.set_footer(text=self.footer)

        await ctx.send(embed=embed)


    # Set the admin role to mention for info 
    @commands.has_role("QOTD Manager")
    @qotd.command(name="set_admin_role")
    async def set_qotd_admin_role(self, ctx: commands.Context, role: commands.RoleConverter = None):
        """Sets the role to ping for admin info (disable it if none specified)"""

        emote = discord.utils.get(ctx.guild.emojis, id=1147153985275437056)

        if role is not None:
            self.admin_role_id = role.id
            description = f'Will ping {role.mention} for admin news '
        else:
            self.admin_role_id = None
            description = f'No role will be pinged for admin news '

        self.save_conf()

        embed = discord.Embed(
            title="Update admin role",
            description=f"{description}{emote}",
            colour=discord.Colour.dark_green()
        )
        embed.set_footer(text=self.footer)

        await ctx.send(embed=embed)


    # Set the channel for qotd
    @commands.has_role("QOTD Manager")
    @qotd.command(name="set_threshold")
    async def set_qotd_warning_threshold(self, ctx: commands.Context, threshold: int):
        """Sets the number of questions at which it starts to warn admins about low questions count"""

        self.warning_threshold = threshold
        self.save_conf()

        description = f"Admins will be warned when there's less than {threshold} questions left "
        emote = discord.utils.get(ctx.guild.emojis, id=1157946531773681704)

        embed = discord.Embed(
            title="Update threshold",
            description=f"{description}{emote}",
            colour=discord.Colour.dark_green()
        )
        embed.set_footer(text=self.footer)

        await ctx.send(embed=embed)


    # Show bot configuration
    @commands.has_role("QOTD Manager")
    @qotd.command(name="conf")
    async def qotd_conf(self, ctx: commands.Context):
        """Shows the QOTD configuration"""

        base = datetime.now()
        iter = aiocron.croniter(self.time, base)
        ts = int(iter.get_next(datetime).timestamp())
        time_desc = f"The question of the day cron schedule is `{self.time}`.\nWhich means the next question will be posted on <t:{ts}:f>."

        if self.channel_id is not None:
            channel = self.bot.get_channel(self.channel_id)
            qotd_channel_desc = f"Questions will be sent to {channel.mention}."
        else:
            qotd_channel_desc = f":warning: **No QOTD channel configured !** Use `?qotd set_channel <channel>`."

        if self.react_channel_id is not None:
            react_channel = self.bot.get_channel(self.react_channel_id)
            react_channel_desc = f"People will be told to discuss in {react_channel.mention}."
        else:
            react_channel_desc = f"No discussion channel configured."

        ping_role = None
        if self.ping_role_id is not None:
            ping_role = ctx.guild.get_role(self.ping_role_id).mention
        if ping_role is not None:
            ping_role_desc = f"{ping_role} will be pinged when sending QOTD."
        else:
            ping_role_desc = "No role will be pinged."

        if self.admin_channel_id is not None:
            admin_channel = self.bot.get_channel(self.admin_channel_id)
            if admin_channel is not None:
                admin_channel_desc = f"Admin warnings will be sent to {admin_channel.mention}."

                role = None
                if self.admin_role_id is not None:
                    role = admin_channel.guild.get_role(self.admin_role_id).mention

                if role is not None:
                    admin_role_desc = f"{role} will be pinged for admin warnings."
                else:
                    admin_role_desc = "No role will be pinged."

                threshold_desc = f"Admins will be pinged if there's {self.warning_threshold} questions or less queued."
            else:
                admin_channel_desc = "Invalid admin channel setup."
                admin_role_desc = "Invalid admin channel setup."
                threshold_desc = "Invalid admin channel setup."
        else:
                admin_channel_desc = "No admin channel setup."
                admin_role_desc = "No admin channel setup."
                threshold_desc = "No admin channel setup."


        embed = discord.Embed(
            title="QOTD configuration",
            colour=discord.Colour.dark_green()
        )
        embed.set_footer(text=self.footer)

        embed.add_field(name="Questions", value=f"There are currently {len(self.questions)} questions queued.")
        embed.add_field(name="Schedule", value=time_desc)
        embed.add_field(name="QOTD channel", value=qotd_channel_desc)
        embed.add_field(name="React channel", value=react_channel_desc)
        embed.add_field(name="Ping role", value=ping_role_desc)
        embed.add_field(name="Admin channel", value=admin_channel_desc)
        embed.add_field(name="Admin role", value=admin_role_desc)
        embed.add_field(name="Warning threshold", value=threshold_desc)

        await ctx.send(embed=embed)


    # Set the role to mention for qotd
    @commands.has_role("QOTD Manager")
    @qotd.command(name="preview")
    async def preview_qotd(self, ctx: commands.Context, number: int = None):
        """Previews a question of the day"""

        if number is None:
            number = len(self.questions)

        if number > 0 and number <= len(self.questions):
            idx = number - 1
            question = self.questions[idx]

            react_emotes, embed = self.make_question(question, ctx.guild)
            embed.set_footer(text="Emotes and image are random and will differ when the question is sent")

            message = await ctx.send(embed=embed)

            for emote in react_emotes:
                await message.add_reaction(emote)
        else:
            description = f"Question number {number} doesn't exist "
            emote = discord.utils.get(ctx.guild.emojis, id=1156319608630935584)
            colour = discord.Colour.red()

            embed = discord.Embed(
                title="Preview error",
                description=f"{description}{emote}",
                colour=colour
            )
            embed.set_footer(text=self.footer)

            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(QOTDs(bot))
