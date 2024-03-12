import datetime
import hashlib
import io
import json
import os
import random
import re
import uuid
from typing import Optional

import asyncio
import discord
import requests
from discord.ext import commands
from discord.utils import get
from PIL import Image

from core import checks
from core.models import PermissionLevel, getLogger
from core.paginator import EmbedPaginatorSession

logger = getLogger(__name__)


COG_NAME = "MentalIllness"
DIR = os.path.dirname(__file__)
SAVE_FILE = os.path.join(os.getcwd(), "mental-illness.json")

CHANNEL_IDS = [1106791361157541898, 781551409433673748]


class MentalIllness(commands.Cog, name=COG_NAME):
    """Earn currency, spend in shops, and win roles!"""

    save: dict[str, object]
    words: dict[str, dict[str, int]]

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cog_id = uuid.uuid4()

        self.save = {}
        if os.path.exists(SAVE_FILE):
            self.load_conf()
        else:
            self.save["words"] = {}
        self.words = self.save["words"]

        self.msg_counter = 0

        self.bot.loop.create_task(self.schedule_save())

        self.footer = ""  # TODO: added just in case we do something with it someday

    def generate_message(self):
        words = [random.choice(list(self.words.keys()))]
        while words[-1] != "\n" or len(words) < 20:
            print(words)
            total = sum(self.words[words[-1]].values())
            probas = {}
            last = 0
            for k, v in self.words[words[-1]].items():
                probas[k] = (last + v) / total
                last += v

            rnd = random.random()
            for w in probas:
                if probas[w] > rnd:
                    words.append(w)
                    break

        return " ".join(words)


    def load_conf(self):
        with open(SAVE_FILE, "r") as f:
            self.save = json.load(f)


    def save_conf(self):
        with open(SAVE_FILE, "w+") as f:
            json.dump(self.save, f)


    async def schedule_save(self):
        while True:
            cog: MentalIllness = self.bot.get_cog(COG_NAME)
            if cog is None or cog.cog_id != self.cog_id:
                # We are in an old cog after update and don't have to send QOTD anymore
                break
            sleep = 60
            await asyncio.sleep(sleep)
            self.save_conf()


    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if message.channel.id in CHANNEL_IDS:
            self.msg_counter += 1

            words = re.split(r"\s+", message.content.lower(), flags=re.MULTILINE) + ["\n"]

            for i in range(len(words) - 1):
                word = words[i]
                nxt = words[i+1]

                if word not in self.words:
                    self.words[word] = {}

                if nxt not in self.words[word]:
                    self.words[word][nxt] = 1
                else:
                    self.words[word][nxt] += 1

        if self.msg_counter == 10 or self.bot.user.mentioned_in(message) \
        or (message.reference and message.reference.resolved.author.id == self.bot.user.id):
            await message.channel.send(self.generate_message())

        if self.msg_counter == 10:
            self.msg_counter = 0



async def setup(bot):
    await bot.add_cog(MentalIllness(bot))
