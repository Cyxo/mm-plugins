import asyncio
import hashlib
import importlib
import json
import os
import random
import sys
import traceback
import uuid
from datetime import datetime, timedelta
from functools import reduce, wraps
from io import BytesIO

import discord
from dotenv import load_dotenv
import requests
from discord.ext import commands
from discord import app_commands
from PIL import Image, ImageDraw, ImageFont

from core import checks
from core.models import PermissionLevel
from core.paginator import EmbedPaginatorSession

sys.path.append(os.path.dirname(__file__))
import player
importlib.reload(player)
import gatos
importlib.reload(gatos)
import team
importlib.reload(team)
import data
importlib.reload(data)


COG_NAME = "GatoGame"
DIR = os.path.dirname(__file__)
SAVE_FILE = os.path.join(os.getcwd(), "gato_beta.json")
CURRENCY_SAVE_FILE = os.path.join(os.getcwd(), "currency.json")
CURRENCY_NAME = "Plum Blossom"
CURRENCY_EMOJI = "🌸"

NERFED_CHANNELS = [1106794426711408700]


def hash2(s: str):
    return hashlib.md5(s.encode()).hexdigest()


def get_image_from_url(url) -> Image.Image:
    r = requests.get(url)
    return Image.open(BytesIO(r.content)).convert("RGBA")


def discord_send_file(file: BytesIO) -> str:
    files = {
        'payload_json': (None, '{"username": "test", "content": "hello"}'),
        'file1': file
    }

    url = os.getenv('GATO_WEBHOOK_URL', '')
    response = requests.post(url[1:-1], files=files)

    return response.json()["attachments"][0]["proxy_url"]


class PullView(discord.ui.View):

    frames: list[dict] = []
    current_frame: int = 0
    title: str
    results: list[gatos.Gato]
    result_lines: list[str]
    result_image: str
    banner: data.Banner
    gato_game: "GatoGame"

    channel: discord.TextChannel
    ctx: commands.Context
    author: discord.User
    message: discord.Message
    ongoing: bool = True
    skipped_yet: bool = False

    def __init__(self, ctx: commands.Context, author: discord.User, anims: list[dict], results: list[gatos.Gato], result_lines: list[str], banner: data.Banner, gato_game: "GatoGame"):
        super().__init__()
        self.frames = anims
        self.ctx = ctx
        self.channel = ctx.channel
        self.author = author
        self.title = f"{self.author.display_name}'s pull"
        self.results = results
        self.result_lines = result_lines
        self.banner = banner
        self.gato_game = gato_game
        self.result_image = None

        if len(result_lines) > 1:
            self.gato_game.bot.loop.run_in_executor(None, self.create_image)

    def create_image(self):
        recap = Image.open(os.path.join(DIR, "gachabg.png"))
        for i in range(len(self.result_lines)):
            item = self.results[i]
            itm = get_image_from_url(item.IMAGE).resize((92, 92))
            recap.paste(itm, (30 * (1+(i % 5)) + 92 * (i % 5), 60 * (1+(i // 5)) + 92 * (i // 5)), itm)
        bio = BytesIO()
        recap.save(bio, format="PNG")
        bio.seek(0)
        self.result_image = discord_send_file(bio)

    async def handle_frame(self, frame: int, skipping=False):
        if skipping:
            self.skipped_yet = True

        if frame == len(self.frames):
            while len(self.frames) > 1 and self.result_image is None:
                await asyncio.sleep(0.5)

            self.ongoing = False
            self.stop()
            description="\n".join(self.result_lines) # Old recap text before recap images
            # description = None # New recap "text"
            pull_again_view = PullAgainView(self.ctx, self.message, self.banner, self.gato_game)
            await pull_again_view.refresh_buttons()
            if len(self.frames) == 1:
                embed = discord.Embed(title=self.title, colour=discord.Colour.teal())
                if skipping:
                    embed.set_image(url=self.frames[0]["solo"])
                    await self.message.edit(embed=embed, view=pull_again_view)
                    await asyncio.sleep(self.frames[0]["solo_duration"] + 2)
                    embed.description = description
                    embed.set_image(url=self.frames[0]["static"])
                    await self.message.edit(embed=embed)
                else:
                    embed.description = description
                    embed.set_image(url=self.frames[0]["static"])
                    await self.message.edit(embed=embed, view=pull_again_view)
            else:
                embed = discord.Embed(title=self.title, colour=discord.Colour.teal(), description=description)
                embed.set_image(url=self.result_image)
                await self.message.edit(embed=embed, view=pull_again_view)
        else:
            embed = discord.Embed(title=self.title, colour=discord.Colour.teal())
            if skipping:
                embed.set_image(url=self.frames[frame]["static"])
                await self.message.edit(embed=embed, view=self)
            else:
                embed.set_image(url=self.frames[frame]["anim"])
                await self.message.edit(embed=embed, view=self)
                await asyncio.sleep(self.frames[frame]["duration"] + 3)
                self.skipped_yet = True
                if self.current_frame == frame:
                    if len(self.frames) == 1:
                        await self.handle_frame(1)
                    else:
                        embed.set_image(url=self.frames[frame]["static"])
                        await self.message.edit(embed=embed, view=self)

    async def first_frame(self):
        self.message = await self.channel.send(self.author.mention)
        await self.handle_frame(0, skipping=False)

    async def on_error(self, interaction, error, item) -> None:
        await self.gato_game.on_error(interaction, error)

    async def on_timeout(self):
        await self.handle_frame(len(self.frames))

    @discord.ui.button(style=discord.ButtonStyle.blurple, emoji="▶️")
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Next item."""
        if interaction.user.id != self.author.id:
            embed = discord.Embed(colour=discord.Colour.red(), description="Only the person pulling can interact.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer()
        if not self.skipped_yet:
            if len(self.frames) == 1:
                self.current_frame += 1
            await self.handle_frame(self.current_frame, skipping=True)
        else:
            self.current_frame += 1
            await self.handle_frame(self.current_frame)

    @discord.ui.button(style=discord.ButtonStyle.blurple, emoji="⏩")
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Skip pulls to result."""
        if interaction.user.id != self.author.id:
            embed = discord.Embed(colour=discord.Colour.red(), description="Only the person pulling can interact.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer()
        self.current_frame = len(self.frames)
        await self.handle_frame(self.current_frame, skipping=True)


class PullAgainView(discord.ui.View):

    banner: data.Banner

    message: discord.Message
    banners_view: "BannersView"

    def __init__(self, ctx: commands.Context, message: discord.Message, banner: data.Banner, gato_game):
        super().__init__()
        self.banner = banner
        self.banners_view = BannersView(ctx, [banner], None, gato_game)
        self.message = message

    async def on_timeout(self) -> None:
        self.stop()
        await self.message.edit(view=None)

    async def refresh_buttons(self):
        pull_cost = self.banner.pull_cost
        btn: discord.ui.Button
        for btn in self.children:
            if btn.custom_id == "1pull":
                btn.label = f"{pull_cost} - Pull 1"
            elif btn.custom_id == "10pull":
                btn.label = f"{pull_cost*10} - Pull 10"
        await self.message.edit(view=self)

    @discord.ui.button(style=discord.ButtonStyle.green, custom_id="1pull", label="... - Pull 1", emoji="🌸")
    async def single(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await self.banners_view.start_pulls(interaction, 1)

    @discord.ui.button(style=discord.ButtonStyle.green, custom_id="10pull", label="... - Pull 10", emoji="🌸")
    async def multi(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await self.banners_view.start_pulls(interaction, 10)


class BannersView(discord.ui.View):

    banners: list[data.Banner]
    current_banner: int
    gato_game: "GatoGame"

    author_id: int
    ctx: commands.Context
    message: discord.Message

    def __init__(self, ctx: commands.Context, banners: list[data.Banner], message: discord.Message, gato_game: "GatoGame"):
        super().__init__()
        self.banners = banners
        self.current_banner = 0
        self.message = message
        self.ctx = ctx
        self.author_id = ctx.author.id
        self.gato_game = gato_game

    async def refresh_embed(self):
        desc = " | ".join([
            bann.name if i != self.current_banner else f"**{bann.name}**" for i, bann in enumerate(self.banners)
        ])
        embed = discord.Embed(
            title="Gacha banners",
            description=desc,
            colour=self.banners[self.current_banner].colour
        )
        embed.set_image(url=self.banners[self.current_banner].img)
        await self.message.edit(content="", embed=embed)

    async def on_error(self, interaction, error, item) -> None:
        await self.gato_game.on_error(interaction, error)

    async def on_timeout(self) -> None:
        self.stop()
        embed = discord.Embed(
            title="Gacha banners",
            description="This view has expired. Use `/critter pull` to show one again!"
        )
        await self.message.edit(embed=embed, view=None)

    async def refresh_buttons(self):
        pull_cost = self.banners[self.current_banner].pull_cost
        btn: discord.ui.Button
        for btn in self.children:
            if btn.custom_id == "1pull":
                btn.label = f"{pull_cost} - Pull 1"
            elif btn.custom_id == "10pull":
                btn.label = f"{pull_cost*10} - Pull 10"
            elif btn.custom_id == "left":
                btn.disabled = True if self.current_banner == 0 else False
            elif btn.custom_id == "right":
                btn.disabled = True if self.current_banner+1 == len(self.banners) else False
        await self.message.edit(view=self)

    async def start_pulls(self, interaction: discord.Interaction, pull_count: int):
        player_id = interaction.user.id

        if player_id not in self.gato_game.players or self.gato_game.players[player_id].currency < self.banners[self.current_banner].pull_cost * pull_count:
            await interaction.followup.send(embed=discord.Embed(
                title="You're broke!!",
                description=f"You don't have enough {CURRENCY_EMOJI} {CURRENCY_NAME}s to pull on this banner! <a:RuanMeiBugcatBroke:1181134215446806579> Check your balance with `/critter balance`.",
                colour=discord.Colour.red()
            ), ephemeral=True)
            return

        player = self.gato_game.players[player_id]

        ongoing_pulls = self.gato_game.players[player_id]._pull_view
        if ongoing_pulls is not None and ongoing_pulls.ongoing:
            description = f"You already have an ongoing pull, please be patient!"
            embed = discord.Embed(
                title="Error",
                description=description.strip(),
                colour=discord.Colour.red()
            )
            await self.ctx.send(embed=embed)
            return

        anims_lists = []
        anims_lists = []
        bann = self.banners[self.current_banner]
        pull_results = bann.get_pulls_results(pull_count, player)
        max_rarity = max(itm.RARITY for itm in pull_results)

        nursery = player.nursery

        player.currency -= pull_count * bann.pull_cost

        result_lines = []
        item: gatos.Item
        for item in pull_results:
            line = await self.gato_game.give_item_to_player(self.ctx, interaction.user, str(item.__name__), 1)
            if "already has **E6" in line:
                cpr = {
                    6: 10*bann.pull_cost,
                    5: 5*bann.pull_cost,
                    4: 1*bann.pull_cost,
                    3: bann.pull_cost//2
                }
                money = cpr[item.RARITY]
                player.currency += money
                result_lines.append(f"- {line}. You received **{money}** {CURRENCY_EMOJI} in compensation.")
            else:
                result_lines.append(f"- {line}")
            # if str(item.ITEM_TYPE) == str(gatos.ABaseItem.ItemType.GATO):
            #     gato: gatos.Gato = item
            #     thegato: gatos.Gato = None
            #     for g in nursery:
            #         if isinstance(g, gato):
            #             thegato = g
            #     if thegato is None:
            #         thegato = gato(name=f"{interaction.user.name}'s {gato.DISPLAY_NAME}")
            #         nursery.append(thegato)
            #         result_lines.append(f"- **{gato.DISPLAY_NAME}** obtained!")
            #     elif thegato.eidolon < 6:
            #         thegato.set_eidolon(thegato.eidolon + 1)
            #         result_lines.append(f"- **{thegato.name}**'s eidolon level increased to **E{thegato.eidolon}**!")
            #     else:
            #         cpr = {
            #             6: 10*bann.pull_cost,
            #             5: 5*bann.pull_cost,
            #             4: 1*bann.pull_cost,
            #             3: bann.pull_cost//2
            #         }
            #         money = cpr[thegato.RARITY]
            #         player.currency += money
            #         result_lines.append(f"- **{thegato.name}** is already **E6**. You received **{money}** {CURRENCY_EMOJI} in compensation.")
            # else:
            #     class_name = item.__name__
            #     if class_name not in player.inventory:
            #         player.inventory[class_name] = 1
            #     else:
            #         player.inventory[class_name] += 1
            #     result_lines.append(f"- {item.DISPLAY_NAME}")

        for i, gato in enumerate(pull_results):
            anim_name: str
            if i == 0:
                anim_name = f"train{max_rarity}"
            else:
                anim_name = "solo"

            anims_lists.append({
                "anim": data.Data.animations[gato.ANIMATIONS][anim_name]["url"],
                "solo": data.Data.animations[gato.ANIMATIONS]["solo"]["url"],
                "static": data.Data.animations[gato.ANIMATIONS]["static"]["url"],
                "duration": data.Data.animations[gato.ANIMATIONS][anim_name]["duration"],
                "solo_duration": data.Data.animations[gato.ANIMATIONS]["solo"]["duration"],
            })

        pv = PullView(self.ctx, interaction.user, anims_lists, pull_results, result_lines, bann, self.gato_game)
        player._pull_view = pv
        await pv.first_frame()


    @discord.ui.button(style=discord.ButtonStyle.blurple, custom_id="left", emoji="⬅️")
    async def left(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            embed = discord.Embed(colour=discord.Colour.red(), description="Only the person who did the command can interact with this.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer()
        self.current_banner -= 1
        if self.current_banner < 0:
            self.current_banner = 0
        await self.refresh_buttons()
        await self.refresh_embed()

    @discord.ui.button(style=discord.ButtonStyle.gray, label="Details", emoji="📄")
    async def details(self, interaction: discord.Interaction, button: discord.ui.Button):
        bann = self.banners[self.current_banner]
        embed = discord.Embed(
            title=f"{bann.name} - Details",
            description=bann.get_rates_text(),
            colour=bann.colour
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(style=discord.ButtonStyle.green, custom_id="1pull", label="... - Pull 1", emoji="🌸")
    async def single(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await self.start_pulls(interaction, 1)

    @discord.ui.button(style=discord.ButtonStyle.green, custom_id="10pull", label="... - Pull 10", emoji="🌸")
    async def multi(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await self.start_pulls(interaction, 10)

    @discord.ui.button(style=discord.ButtonStyle.blurple, custom_id="right", emoji="➡️")
    async def right(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            embed = discord.Embed(colour=discord.Colour.red(), description="Only the person who did the command can interact with this.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer()
        self.current_banner += 1
        if self.current_banner >= len(self.banners):
            self.current_banner = len(self.banners) - 1
        await self.refresh_buttons()
        await self.refresh_embed()


def init_nursery(function):
    """Decorator that creates a nursery for the player if they don't already have one, with a 3-star gato in it."""
    @wraps(function)
    async def new_function(self: "GatoGame", interaction: discord.Interaction, *args, **kwargs):
        self.create_player(interaction.user.id)
        return await function(self, interaction, *args, **kwargs)

    return new_function


@app_commands.guilds(
    311149232402726912,
    1106785082028597258
)
class GatoGame(commands.GroupCog, name=COG_NAME, group_name="critter"):
    """Critter gacha game plugin"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cog_id = uuid.uuid4()
        self.footer = ""  # TODO: REPLACE ME

        print("GATO_WEBHOOK_URL", os.getenv('GATO_WEBHOOK_URL', 'no url'))

        self.players: dict[int, player.Player] = {}
        if not os.path.exists(SAVE_FILE):
            with open(CURRENCY_SAVE_FILE, "r") as f:
                currency_save: dict = json.load(f)
            for id, p in currency_save.items():
                self.create_player(int(id))
                np = self.players[int(id)]
                np.currency = p["currency"]
                np.inventory = p["inventory"]
                np.currency_boost = p["currency_boost"]
            self.save_conf()
        else:
            self.load_conf()

        self.bot.loop.create_task(self.schedule_simulation())
        self.bot.loop.create_task(self.schedule_save())

        shops_save = os.path.join(DIR, "shops_url.json")
        self.shop_images = {}
        if os.path.exists(shops_save):
            with open(shops_save) as f:
                self.shop_images = json.load(f)
        for shop in data.Data.LEGACY_SHOPS:
            n = len(shop.to_buy) // 8 + 1
            for i in range(n):
                filename = f"to_buy_{hash2(json.dumps(shop.to_dict()))}_{i}.png"
                if filename not in self.shop_images.keys():
                    # TODO: "upload" to Discord and retrieve URL
                    print(f"No image for shop {shop.name}-{i}")

        self.__cog_app_commands_group__.on_error = self.on_error


    def compute_vc_currency(self, duration: int):
        # duration in seconds since last compute

        for g in self.bot.guilds:
            for vc in g.voice_channels:
                for member in vc.members:
                    if member.id not in self.players.keys():
                        self.create_player(member.id)
                    player = self.players[member.id]

                    mute = (member.voice.mute or member.voice.self_mute) and not member.voice.suppress
                    deaf = member.voice.deaf or member.voice.self_deaf

                    if deaf:
                        player._vc_earn_rate = 0
                    elif mute:
                        player._vc_earn_rate = 0.5
                    else:
                        player._vc_earn_rate = 0.7

                    boost = 1 + player.currency_boost
                    if any([role.id == 1145893255062495303 for role in member.roles]):
                        boost += 0.1

                    decay = max(1 - player._time_in_vc / (3*60*60), 0.3)

                    if vc.id in NERFED_CHANNELS:
                        player._vc_earn_rate = 0.005
                        decay = 1
                        boost = 1

                    earnings = 100 / 60 * duration * boost * player._vc_earn_rate * decay
                    player.currency += earnings

                    player._time_in_vc += duration


    def load_conf(self):
        with open(SAVE_FILE, "r") as f:
            save: dict = json.load(f)

        for k, v in save.items():
            self.players[int(k)] = player.Player.from_json(v)


    def save_conf(self):
        save = {}
        for k, v in self.players.items():
            save[str(k)] = v.to_json()

        with open(SAVE_FILE, "w+") as f:
            json.dump(save, f)


    async def schedule_save(self):
        while True:
            cog: GatoGame = self.bot.get_cog(COG_NAME)
            if cog is None or cog.cog_id != self.cog_id:
                # We are in an old cog after update and don't have to send QOTD anymore
                break
            sleep = 2
            await asyncio.sleep(sleep)
            self.compute_vc_currency(sleep)
            self.save_conf()


    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        self.create_player(message.author.id)
        player = self.players[message.author.id]

        t = datetime.now()
        if player._last_talked.minute != t.minute or player._last_talked.hour != t.hour or player._last_talked.date() != t.date():
            player._last_talked = t
            player._talked_this_minute = 0

        msg: str = message.content
        if not msg.startswith("?") and player._talked_this_minute < 10:
            filtered = list(filter(lambda w: len(w) > 1, msg.split()))
            score = min(len(filtered), 20)
            boost = 1 + player.currency_boost
            if any([role.id == 1145893255062495303 for role in message.author.roles]):
                boost += 0.1
            
            player.currency += score * boost

            if len(message.stickers) > 0:
                player.currency += 3

            player._talked_this_minute += 1


    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if member.id not in self.players.keys():
            self.create_player(member.id)
        player = self.players[member.id]

        if before.channel is None and after.channel is not None:
            now = datetime.now()
            if now.date() != player._last_day_in_vc.date():
                player._time_in_vc = 0
            player._last_day_in_vc = now


    @init_nursery
    async def nursery_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        choices = []

        player = self.players[interaction.user.id]
        for i, gato in enumerate(sorted(player.nursery, key=lambda a: a.name)):
            if current.lower() in gato.name.lower() or current.lower() in gato.DISPLAY_NAME.lower() or str(i).startswith(current):
                choices.append(app_commands.Choice(name=f"{gato.name} ({gato.DISPLAY_NAME})", value=gato.DISPLAY_NAME))

        return choices[:25]

    @init_nursery
    async def consumables_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        choices = []

        player = self.players[interaction.user.id]

        for itm in sorted(gatos.CONSUMABLES, key=lambda i: i.DISPLAY_NAME):
            if current.lower() in itm.DISPLAY_NAME.lower() \
            and itm.__name__ in player.inventory and player.inventory[itm.__name__] > 0:
                choices.append(
                    app_commands.Choice(name=f"{itm.DISPLAY_NAME} ({player.inventory[itm.__name__]})", value=itm.__name__)
                )

        return choices[:25]


    @init_nursery
    async def equipments_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        choices = []

        player = self.players[interaction.user.id]

        for itm in sorted(gatos.EQUIPMENTS, key=lambda i: i.DISPLAY_NAME):
            if current.lower() in itm.DISPLAY_NAME.lower() \
            and itm.__name__ in player.inventory and player.inventory[itm.__name__] > 0:
                choices.append(
                    app_commands.Choice(name=f"{itm.DISPLAY_NAME} (Critter equipment) ({player.inventory[itm.__name__]})", value=itm.__name__)
                )
        for itm in sorted(gatos.TEAM_EQUIPMENTS, key=lambda i: i.DISPLAY_NAME):
            if current.lower() in itm.DISPLAY_NAME.lower() \
            and itm.__name__ in player.inventory and player.inventory[itm.__name__] > 0:
                choices.append(
                    app_commands.Choice(name=f"{itm.DISPLAY_NAME} (Team equipment) ({player.inventory[itm.__name__]})", value=itm.__name__)
                )
        return choices[:25]


    async def anything_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        choices = [app_commands.Choice(name=itm.DISPLAY_NAME, value=itm_name)
                   for itm_name, itm in sorted(gatos.items_helper.items(), key=lambda i: i[1].DISPLAY_NAME)
                   if current.lower() in itm.DISPLAY_NAME.lower() or current.lower() in itm.__doc__.lower()]
        choices += [app_commands.Choice(name=v.name, value=k)
                    for k, v in sorted(data.Data.LEGACY_ITEMS.items(), key=lambda i: i[1].name)
                    if current.lower() in v.name.lower() or current.lower() in v.description.lower()]
        return choices[:25]


    async def shops_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        choices = []
        for shp in data.Data.LEGACY_SHOPS:
            for itm, price in sorted(shp.to_buy.items(), key=lambda i: i[0]):
                # TODO: Prepare to handle new items later too
                item = data.Data.LEGACY_ITEMS[itm]
                if current.lower() in item.name.lower() or current.lower() in item.description.lower():
                    choices.append(app_commands.Choice(
                        name=f"{item.name} ({CURRENCY_EMOJI} {price})",
                        value=itm
                    ))
        return choices[:25]


    @commands.group(name="critter", invoke_without_command=True, aliases=["gato", "catto", "cake"])
    async def critter(self, ctx: commands.Context):
        """
        Ruan Mei Mains' critter gacha game!
        """

        await ctx.send_help(ctx.command)


    def handle_events(self, plyr: player.Player, team: list[gatos.Gato]):
        lines = []

        for gato in team:
            lines += gato.handle_events(plyr, CURRENCY_EMOJI)

        return "\n".join(lines)


    def create_player(self, player_id):

        if player_id not in self.players:
            p = player.Player()
            gato3s = gatos.NormalGato()
            p.nursery.append(gato3s)
            self.players[player_id] = p


    async def give_item_to_player(self, ctx: commands.Context, member: discord.Member, item_class: str, amount: int = 1):
        plyr = self.players[member.id]

        if item_class in gatos.items_helper and issubclass(gatos.items_helper[item_class], gatos.Gato):
            lines = []
            for _ in range(amount):
                gato: gatos.Gato = discord.utils.find(lambda g: g.__class__.__name__ == item_class, plyr.nursery)
                if gato is None:
                    ng: gatos.Gato = gatos.items_helper[item_class]()
                    plyr.nursery.append(ng)
                    lines.append(f"{member.mention} received a **{ng.DISPLAY_NAME}**")
                elif gato.eidolon < 6:
                    gato.set_eidolon(gato.eidolon + 1)
                    lines.append(f"{member.mention}'s **{gatos.items_helper[item_class].DISPLAY_NAME}** is now at :sparkles: **E{gato.eidolon}**")
                else:
                    lines.append(f":warning: {member.mention} already has **E6 {gatos.items_helper[item_class].DISPLAY_NAME}**")
            return "\n".join(lines)
        else:
            if item_class in data.Data.LEGACY_ITEMS:
                itm = data.Data.LEGACY_ITEMS[item_class]
                for effect, args in itm.effects.items():
                    await eval(f"data.LegacyEffects.{effect}")(plyr, ctx, *args)
                item_name = itm.name
            elif item_class in gatos.items_helper:
                item_name = gatos.items_helper[item_class].DISPLAY_NAME
            else:
                item_name = item_class

            if item_class not in plyr.inventory:
                plyr.inventory[item_class] = amount
            else:
                plyr.inventory[item_class] += amount
            return f"{member.mention} received **{amount} {item_name}**"


    async def schedule_simulation(self):
        while True:
            cog: GatoGame = self.bot.get_cog(COG_NAME)
            if cog is None or cog.cog_id != self.cog_id:
                # We are in an old cog after update and don't have to send QOTD anymore
                break
            sleep = 10
            await asyncio.sleep(sleep)

            for user_id, p in self.players.items():
                if p.deployed_team is None or p.deployed_team.deployed_at is None:
                    continue
                tm = p.deployed_team
                TIME_STEP = 1
                now = datetime.now()
                delta = int((now - tm.deployed_at).total_seconds())
                for _ in range(0, delta, TIME_STEP):
                    if all(gato._fainted for gato in tm.gatos):
                        break

                    for gato in tm.gatos:
                        gato.simulate(tm.gatos, TIME_STEP)

                if any(gato.health < 10 for gato in tm.gatos):
                    if not tm.pinged_already and p.ping:
                        channel = self.bot.get_channel(p.command_channel)
                        embed = discord.Embed(
                            title="Critter expedition",
                            description="**One of your critter has low HP.**\n\nYou can check their status using `/critter team`.\nYou should probably heal them or recall the team using `/critter recall`.",
                            colour=discord.Colour.red()
                        )
                        embed.set_footer(text="If you want to opt out of these pings, use `/critter lifealert`")
                        await channel.send(content=f"<@{user_id}>", embed=embed)
                        tm.pinged_already = True
                else:
                    tm.pinged_already = False
                tm.deployed_at = now


    @app_commands.command(
        name="pull",
        description="List banners and allow to pull on them",
        auto_locale_strings=False
    )
    @init_nursery
    async def banners(self, interaction: discord.Interaction):
        """List banners and allow to pull on them"""
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)

        message = await ctx.send("Loading...")

        bv = BannersView(ctx, data.Data.banners, message, self)
        await bv.refresh_buttons()
        await bv.refresh_embed()


    @app_commands.command(
        name="nursery",
        description="Show your critter nursery",
        auto_locale_strings=False
    )
    @init_nursery
    async def nursery(self, interaction: discord.Interaction):
        """ Show your critter nursery """
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)

        player = self.players[ctx.author.id]

        embeds = [g.get_gato_embed() for g in player.nursery]
        paginator = EmbedPaginatorSession(ctx, *embeds)
        await paginator.run()


    @app_commands.command(
        name="team",
        description="Show your deployed team",
        auto_locale_strings=False
    )
    @init_nursery
    async def team(self, interaction: discord.Interaction):
        """ Show your deployed team """
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)

        player = self.players[ctx.author.id]
        if player.deployed_team is None or player.deployed_team.deployed_at is None:
            embed = discord.Embed(
                title=f"Claim rewards",
                description="No team has been deployed! Check `/critter deploy` to deploy one first!",
                colour=discord.Colour.red()
            )
            await ctx.send(embed=embed)
            return

        embeds = [g.get_gato_embed() for g in player.deployed_team.gatos]
        paginator = EmbedPaginatorSession(ctx, *embeds)
        await paginator.run()


    @app_commands.command(
        name="info",
        description="Show info about a critter or an item",
        auto_locale_strings=False
    )
    @app_commands.autocomplete(itm=anything_autocomplete)
    @init_nursery
    async def info(self, interaction: discord.Interaction, itm: str):
        """ Show info about a critter or an item """
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)

        if itm in gatos.items_helper:
            embed = gatos.items_helper[itm].get_embed()
        else:
            item = data.Data.LEGACY_ITEMS[itm]
            description = f"# {item.name}\n"
            description += item.description + "\n\n"
            description += "**Effects:**\n"
            if len(item.effects.keys()) > 0:
                for effect in item.effects.keys():
                    description += f"- {eval(f'data.LegacyEffects.{effect}').__doc__.format(*item.effects[effect])}\n"
            else:
                description += "*No effect, this item is purely a collectible!*\n"

            embed = discord.Embed(
                title=item.name,
                description=description,
                colour=discord.Colour.teal()
            )
            embed.set_thumbnail(url=item.image)

        await ctx.send(embed=embed)


    @app_commands.command(
        name="deploy",
        description="(Re)deploy a team of critters. ⚠️ Order matters! Critter skills will take effect in deployment order",
        auto_locale_strings=False
    )
    @app_commands.autocomplete(
        critter1=nursery_autocomplete,
        critter2=nursery_autocomplete,
        critter3=nursery_autocomplete,
        critter4=nursery_autocomplete
    )
    @init_nursery
    async def deploy(self, interaction: discord.Interaction, critter1: str = None, critter2: str = None, critter3: str = None, critter4: str = None):
        """ (Re)deploy a team of critters. ⚠️ Order matters! Critter skills will take effect in deployment order (for example, put Critters that boost the whole team in first place). """
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)

        player = self.players[ctx.author.id]
        nursery = player.nursery
        gatos = [critter1, critter2, critter3, critter4]

        player.command_channel = ctx.channel.id

        if all([gato is None for gato in gatos]):
            if player.deployed_team is not None:
                tm = player.deployed_team
                if tm.deployed_at is not None:
                    embed = discord.Embed(
                        title=f"Deploy team",
                        description="A team is already deployed! Use `/critter claim` to see what they fetched for you!",
                        colour=discord.Colour.red()
                    )
                    await ctx.send(embed=embed)
                else:
                    tm.deployed_at = datetime.now()
                    for gato in tm.gatos:
                        gato.deploy(tm.gatos)
                    gato_names = "**, **".join([gato.name for gato in tm.gatos])
                    embed = discord.Embed(
                        title=f"Deploy team",
                        description=f"A team with **{gato_names}** has been deployed! Check back in a while with `/critter claim` to see what they fetched for you!",
                        colour=discord.Colour.teal()
                    )
                    await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title=f"Deploy team",
                    description="No team was previously deployed! Example use `/critter deploy 1 2 3 4` (check critter numbers with `/critter nursery`)",
                    colour=discord.Colour.red()
                )
                await ctx.send(embed=embed)
        else:
            if player.deployed_team is not None and player.deployed_team.deployed_at is not None:
                embed = discord.Embed(
                    title=f"Deploy team",
                    description="A team is already deployed! Use `/critter claim` to see what they fetched for you!",
                    colour=discord.Colour.red()
                )
                await ctx.send(embed=embed)
                return

            # Get unique numbers
            gatos = reduce(lambda re, x: re+[x] if x not in re and x is not None else re, gatos, [])[:4]
            legatos: list = []
            for ga in gatos:
                for g in player.nursery:
                    if g.DISPLAY_NAME == ga:
                        legatos.append(g)
                        break

            tm = team.Team(legatos, deployed_at=datetime.now())
            player.deployed_team = tm
            for gato in tm.gatos:
                gato.deploy(tm.gatos)

            gato_names = "**, **".join([gato.name for gato in legatos])
            embed = discord.Embed(
                title=f"Deploy team",
                description=f"A team with **{gato_names}** has been deployed! Check back in a while with `/critter claim` to see what they fetched for you!",
                colour=discord.Colour.teal()
            )
            await ctx.send(embed=embed)
            return


    @app_commands.command(
        name="claim",
        description="Claim what the deployed team has gathered",
        auto_locale_strings=False
    )
    @init_nursery
    async def claim(self, interaction: discord.Interaction):
        """ Claim what the deployed team has gathered. """
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)

        player = self.players[ctx.author.id]
        player.command_channel = ctx.channel.id

        if player.deployed_team is None or player.deployed_team.deployed_at is None:
            embed = discord.Embed(
                title=f"Claim rewards",
                description="No team has been deployed! Check `/critter deploy` to deploy one first!",
                colour=discord.Colour.red()
            )
            await ctx.send(embed=embed)
            return

        tm = player.deployed_team
        now = datetime.now()
        delta = int((now - tm.deployed_at).total_seconds())
        tm.deployed_at = now

        TIME_STEP = 1
        for _ in range(0, delta, TIME_STEP):
            if all(gato._fainted for gato in tm.gatos):
                break

            for gato in tm.gatos:
                gato.simulate(tm.gatos, TIME_STEP)

        events = self.handle_events(player, tm.gatos)
        currency = 0
        objects = []
        for gato in tm.gatos:
            c, o = gato.claim()
            currency += c
            objects += o

        currency *= 1 + player.currency_boost

        if len(events) == 0:
            events = "*Nothing specific happened.*"
        if len(objects) > 0:
            objnames = [gatos.items_helper[o].DISPLAY_NAME for o in objects]
            objs = "**" + '**, **'.join(set([f"{objnames.count(o)}x {o}" for o in objnames])) + "**"
        else:
            objs = "*no objects*"

        player.currency += currency
        for obj in objects:
            await self.give_item_to_player(ctx, ctx.author, obj, 1)

        embed = discord.Embed(
            title=f"Claim rewards",
            description=f"### Expedition results\nYour critters brought back **{int(currency)}** {CURRENCY_EMOJI} and {objs}.\n### Event log\n{events}",
            colour=discord.Colour.teal()
        )
        await ctx.send(embed=embed)


    @app_commands.command(
        name="recall",
        description="Stops the ongoing expedition and claims the leftover rewards",
        auto_locale_strings=False
    )
    @init_nursery
    async def recall(self, interaction: discord.Interaction):
        await self.claim.callback(self, interaction)
        player = self.players[interaction.user.id]
        if player.deployed_team is not None:
            player.deployed_team.deployed_at = None
            embed = discord.Embed(
                title="Recall",
                description="Team recalled successfully.",
                colour=discord.Colour.teal()
            )
            await interaction.channel.send(embed=embed)


    @app_commands.command(
        name="use",
        description="Use a consumable",
        auto_locale_strings=False
    )
    @app_commands.autocomplete(item=consumables_autocomplete)
    @init_nursery
    async def use(self, interaction: discord.Interaction, item: str, amount: int = 1):
        """ Use a consumable """
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)

        _msg = await ctx.send("Loading...") # Dirty fix for first message not allowed to be ephemeral
        await _msg.delete()

        player = self.players[ctx.author.id]

        if item not in player.inventory or player.inventory[item] < amount:
            await interaction.followup.send(embed=discord.Embed(
                title=f"Not enough {gatos.items_helper[item].DISPLAY_NAME}",
                description=f"You don't have enough of this consumable! Check your inventory with `/critter inventory`.",
                colour=discord.Colour.red()
            ), ephemeral=True)
            return

        for _ in range(amount):
            itm: gatos.Consumable = gatos.items_helper[item]()
            success = await itm.consume(ctx, self)

            if not success:
                break
            else:
                player.inventory[item] -= 1


    @app_commands.command(
        name="equip",
        description="Equip an item",
        auto_locale_strings=False
    )
    @app_commands.autocomplete(item=equipments_autocomplete, critter=nursery_autocomplete)
    @init_nursery
    async def equip(self, interaction: discord.Interaction, item: str, critter: str = None):
        """ Equip an item """
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)

        player = self.players[ctx.author.id]
        itm: gatos.Consumable = gatos.items_helper[item]()

        if item not in player.inventory or player.inventory[item] < 1:
            await interaction.followup.send(embed=discord.Embed(
                title=f"Not enough {itm.DISPLAY_NAME}",
                description=f"You don't have enough of this equipment! Check your inventory with `/critter inventory`.",
                colour=discord.Colour.red()
            ), ephemeral=True)
            return


        if str(itm.ITEM_TYPE) == str(gatos.ABaseItem.ItemType.EQUIPMENT):
            if critter is None:
                embed = discord.Embed(
                    title=f"Using equipment",
                    description="You need to specify a critter to equip this item on!",
                    colour=discord.Colour.red()
                )
                await ctx.send(embed=embed)
                return

            gato: gatos.Gato = None
            for g in player.nursery:
                if g.DISPLAY_NAME == critter:
                    gato = g
            if gato is None:
                embed = discord.Embed(
                    title=f"Using equipment",
                    description=f'Critter "{critter}" not found! What are you trying to do...',
                    colour=discord.Colour.red()
                )
                await ctx.send(embed=embed)
                return
            gato.equipments.append(itm)
            embed = discord.Embed(
                title="Equipment",
                description=f"**{itm.DISPLAY_NAME}** was sucessfully equiped to **{gato.name}**!",
                colour=discord.Colour.teal()
            )
            await ctx.send(embed=embed)

            player.inventory[item] -= 1
        elif str(itm.ITEM_TYPE) == str(gatos.ABaseItem.ItemType.TEAM_EQUIPMENT):
            if player.deployed_team is None or player.deployed_team.deployed_at is None:
                embed = discord.Embed(
                    title=f"Using team equipment",
                    description="No team has been deployed! Check `/critter deploy` to deploy one first!",
                    colour=discord.Colour.red()
                )
                await ctx.send(embed=embed)
                return

            tm = player.deployed_team
            for g in tm.gatos:
                g.equipments.append(itm)
            embed = discord.Embed(
                title="Team equipment",
                description=f"**{itm.DISPLAY_NAME}** was sucessfully equiped to deployed team!",
                colour=discord.Colour.teal()
            )
            await ctx.send(embed=embed)

            player.inventory[item] -= 1


    @app_commands.command(
        name="rename",
        description="Rename your critter"
    )
    @app_commands.autocomplete(critter=nursery_autocomplete)
    @init_nursery
    async def rename(self, interaction: discord.Interaction, critter: str, name: str):
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)

        gato: gatos.Gato = None
        for g in player.nursery:
            if g.DISPLAY_NAME == critter:
                gato = g
        if gato is None:
            embed = discord.Embed(
                title=f"Using equipment",
                description=f'Critter "{critter}" not found! What are you trying to do...',
                colour=discord.Colour.red()
            )
            await ctx.send(embed=embed)
            return
        gato.name = name

        embed = discord.Embed(
            title="Rename success",
            description=f'Your *{gato.DISPLAY_NAME}* has been successfully renamed "{gato.name}"',
            colour=discord.Colour.teal()
        )
        await ctx.send(embed=embed)


    @app_commands.command(
        name="lifealert",
        description="Opt in/out of low HP pings",
        auto_locale_strings=False
    )
    @init_nursery
    async def lifealert(self, interaction: discord.Interaction, enabled: bool):
        """Opt in/out of low HP pings"""
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)

        player = self.players[ctx.author.id]
        player.ping = enabled

        if enabled:
            description = "Ping on low HP have been enabled"
        else:
            description = "Ping on low HP have been disabled. You can always enable them back with `/critter lifealert`"

        embed = discord.Embed(
            title="Low HP pings",
            description=description,
            colour=discord.Colour.teal()
        )
        await ctx.send(embed=embed, ephemeral=True)


    @app_commands.command(
        name="fastforward",
        description="Fastforward the ongoing Gato expedition by a specified amount of time (in seconds)",
        auto_locale_strings=False
    )
    @init_nursery
    async def ff(self, interaction: discord.Interaction, seconds: int):
        """ Fastforward the ongoing Gato expedition by a specified amount of time (in seconds) """
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)

        player = self.players[ctx.author.id]
        if player.deployed_team is None or player.deployed_team.deployed_at is None:
            embed = discord.Embed(
                title=f"Claim rewards",
                description="No team has been deployed! Check `/critter deploy` to deploy one first!",
                colour=discord.Colour.red()
            )
            await ctx.send(embed=embed)
            return

        tm = player.deployed_team
        tm.deployed_at -= timedelta(seconds=seconds)

        await ctx.send("Done! ✅")


    @app_commands.command(
        name="give",
        description="Give items or currency to a user or yourself"
    )
    @app_commands.autocomplete(item=anything_autocomplete)
    @app_commands.checks.has_any_role(
        692818953604562964,     # Staff role for Ruan Dev
        1117348317790224434,    # Bot Lead Dev
        1106785500167155763,    # drinking tea is good
        1106786509991977000,    # Meihua (Admins)
        1106789830626639882     # Staff (remove after beta)
    )
    async def give(self, interaction: discord.Interaction, amount: int = 1, member: discord.Member = None, item: str = None):
        """ Give items or currency to a user or yourself """
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)

        if member is None:
            member = ctx.author

        self.create_player(member.id)
        player = self.players[member.id]

        if item is None:
            player.currency += amount
            description = f"{member.mention} received **{amount}** {CURRENCY_EMOJI}"
        else:
            description = await self.give_item_to_player(ctx, member, item, amount)

        await ctx.send(embed=discord.Embed(title="Give", description=description, colour=discord.Colour.teal()))


    @app_commands.command(
        name="balance",
        description=f"Check your (or someone else's) {CURRENCY_EMOJI} {CURRENCY_NAME} balance"
    )
    @init_nursery
    async def balance(self, interaction: discord.Interaction, member: discord.Member = None):
        """Shows a user's currency balance"""
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)

        if member is None:
            member = ctx.author

        if member.id in self.players:
            player = self.players[member.id]
            description = f"{member.display_name} currently has {int(player.currency)} {CURRENCY_EMOJI}"
            colour = discord.Colour.teal()
        else:
            description = f"{member.display_name} isn't in our database. Have they ever talked??"
            colour = discord.Colour.red()

        embed = discord.Embed(
            title=f"{member.display_name}'s money",
            description=f"{description}",
            colour=colour
        )
        embed.set_footer(text=self.footer)

        await ctx.send(embed=embed)


    # Items and currencies inventory
    @app_commands.command(
        name="inventory",
        description=f"Check your (or someone else's) inventory"
    )
    @init_nursery
    async def inventory(self, interaction: discord.Interaction, member: discord.Member = None):
        """Shows a user's inventory"""
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)

        if member is None:
            member = ctx.author

        descriptions = []
        if member.id in self.players:
            player = self.players[member.id]

            description = "## Items:\n"
            i = 0
            lines = []
            for item, amount in player.inventory.items():
                i += 1
                if item in data.Data.LEGACY_ITEMS:
                    itm = data.Data.LEGACY_ITEMS[item]
                    lines.append(f"- **{itm.name}** x{amount}")
                elif item in gatos.items_helper:
                    itm = gatos.items_helper[item]
                    lines.append(f"- **{itm.DISPLAY_NAME}** x{amount}")
                else:
                    lines.append(f"- **{item}** x{amount}")
            if i == 0:
                lines.append("This user has no items in their inventory.")
            lines.sort()

            lns = []
            for i, line in enumerate(lines):
                lns.append(line)
                if len(lns) == 10 or i == len(lines) - 1:
                    descriptions.append(description + "\n".join(lns))
                    lns = []

            colour = discord.Colour.teal()
        else:
            descriptions = [f"{member.display_name} isn't in our database. Have they ever talked??"]
            colour = discord.Colour.red()

        embeds = []
        for description in descriptions:
            embed = discord.Embed(
                title=f"{member.display_name}'s inventory",
                description=description,
                colour=colour
            )
            embed.set_footer(text=self.footer)
            embeds.append(embed)
        paginator = EmbedPaginatorSession(ctx, *embeds)
        await paginator.run()


    # Gamble currency in heads/tails
    @app_commands.command(
        name="flip",
        description=f"Gamble currency by flippîng a coin"
    )
    @app_commands.choices(guess=[
        app_commands.Choice(name="Heads", value="heads"),
        app_commands.Choice(name="Tails", value="tails")
    ])
    @init_nursery
    async def flip(self, interaction: discord.Interaction, guess: str, money: int):
        """ Gamble currency by flippîng a coin """
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)

        player = None
        if ctx.author.id in self.players.keys():
            player = self.players[ctx.author.id]

        img = None

        if guess.lower() not in ["heads", "tails"]:
            description = f"Stop kidding with your `{guess}`! Guess one of these: `heads/h/tails/t`"
            colour = discord.Colour.red()
        elif player is None:
            description = "You don't have any money. Try talking a little before trying to gamble, okay?"
            colour = discord.Colour.red()
        elif money < 0 or money > player.currency:
            description = f"Can't bet **{money}** {CURRENCY_EMOJI}. Try checking your balance with `/critter balance`"
            colour = discord.Colour.red()
        else:
            colour = discord.Colour.teal()
            description = "Ruan Mei flips a coin, and it falls on... "
            rnd = random.randint(0, 10000)
            if rnd < 5000:
                description += "Heads!\n"
                if guess.lower() == "heads":
                    player.currency += money
                    description += "You won! You get double what you bet!"
                    img = "https://cdn.discordapp.com/emojis/1164689665740259369.gif"
                else:
                    player.currency -= money
                    description += "You lost :frowning: You lost everything you bet, try again next time!"
                    img = "https://cdn.discordapp.com/emojis/1188293763718709258.webp"
            elif rnd < 10000:
                description += "Tails!\n"
                if guess.lower() == "tails":
                    player.currency += money
                    description += "You won! You get double what you bet!"
                    img = "https://cdn.discordapp.com/emojis/1164689665740259369.gif"
                else:
                    player.currency -= money
                    description += "You lost :frowning: You lost everything you bet, try again next time!"
                    img = "https://cdn.discordapp.com/emojis/1188293763718709258.webp"
            else:
                colour = discord.Colour.gold()
                description += "its edge!\nWow, who could've guessed that?? Anyway, you get your coins back!"
                img = "https://cdn.discordapp.com/emojis/1171830972786933850.webp"
        
        embed = discord.Embed(
            title=f'Coin flip',
            description=description,
            colour=colour
        )
        if img is not None: embed.set_thumbnail(url=img)
        embed.set_footer(text=self.footer)
        await ctx.send(embed=embed)


    # Gamble currency in rock paper scissors
    @app_commands.command(
        name="rps",
        description=f"Gamble currency by playing Rock Paper Scissors against Ruan Mei"
    )
    @app_commands.choices(move=[
        app_commands.Choice(name="Rock", value="rock"),
        app_commands.Choice(name="Paper", value="paper"),
        app_commands.Choice(name="Scissors", value="scissors"),
    ])
    @init_nursery
    async def rps(self, interaction: discord.Interaction, move: str, money: int):
        """ Gamble currency by playing Rock Paper Scissors """
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)

        adjectives = ["an epic", "a grand", "a heroic", "a monumental", "an extravagant", "a bombastic", "an ambitious", "an arduous", "a huge", "an extraordinary"]
        battles = ["battle", "duel", "clash", "fight", "confrontation", "encounter", "skirmish", "contest"]

        player = None
        if ctx.author.id in self.players.keys():
            player = self.players[ctx.author.id]

        img = None

        if move.lower() not in ["rock", "paper", "scissors"]:
            description = f"Hey! `{move}` is not a valid move in Rock Paper Scissors! Pick one of these: Rock / Paper / Scissors"
            colour = discord.Colour.red()
        elif player is None:
            description = "You don't have any money. Try talking a little before trying to gamble, okay?"
            colour = discord.Colour.red()
        elif money < 0 or money > player.currency:
            description = f"Can't bet **{money}** {CURRENCY_EMOJI}. Try checking your balance with `/critter balance`"
            colour = discord.Colour.red()
        else:
            rmove = random.choice(["rock", "paper", "scissors"])

            colour = discord.Colour.teal()
            description = f"You pick {random.choice(adjectives)} {random.choice(battles)} of Rock Paper Scissors against Ruan Mei!\n"
            description += f"The tension is at its highest as **{money}** {CURRENCY_EMOJI} are at stake on each side...\n\n"
            description += f"You play *{move}*.\n"
            description += f"She plays *{rmove}*.\n\n"
            if move == "rock" and rmove == "paper" \
            or move == "paper" and rmove == "scissors" \
            or move == "scissors" and rmove == "rock":
                description += f"You crumble in tears as you lose your **{money}** {CURRENCY_EMOJI}..."
                player.currency -= money
                img = "https://cdn.discordapp.com/emojis/1188293763718709258.webp"
            elif move == rmove:
                description += f"It's a tie! Everyone gets their money back."
                img = "https://cdn.discordapp.com/emojis/1171830972786933850.webp"
            else:
                description += f"You did it! You won! You receive **{money*2}** {CURRENCY_EMOJI} for your victory!"
                player.currency += money
                img = "https://cdn.discordapp.com/emojis/1164689665740259369.gif"
        
        embed = discord.Embed(
            title=f'Rock Paper Scissors',
            description=description,
            colour=colour
        )
        if img is not None: embed.set_thumbnail(url=img)
        embed.set_footer(text=self.footer)
        await ctx.send(embed=embed)


    @app_commands.command(
        name="shops",
        description=f"Shows what's to buy in the shops"
    )
    @init_nursery
    async def shops(self, interaction: discord.Interaction):
        """Shows what's to buy in the shops"""
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)

        embeds = []
        for shop in data.Data.LEGACY_SHOPS:
            n = len(shop.to_buy) // 8 + 1
            for i in range(n):
                embed = discord.Embed(
                    title="Items to buy",
                    description=f"## Items to buy - {shop.name} ({i+1}/{n})",
                    colour=discord.Colour.green()
                )

                filename = f"to_buy_{hash2(json.dumps(shop.to_dict()))}_{i}.png"
                if filename in self.shop_images.keys():
                    embed.set_image(url=self.shop_images[filename])
                else:
                    embed.set_footer(text="ERROR: No image for this shop. Please ping @cyxo")
                embeds.append(embed)

        paginator = EmbedPaginatorSession(ctx, *embeds)
        await paginator.run()


    @app_commands.command(
        name="buy",
        description=f"Buy an item at the shop"
    )
    @app_commands.autocomplete(item=shops_autocomplete)
    @init_nursery
    async def buy(self, interaction: discord.Interaction, item: str, amount: int = 1):
        """Buy an item at the shop"""
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        
        player = self.players[ctx.author.id]

        price = None
        for shp in data.Data.LEGACY_SHOPS:
            if item in shp.to_buy:
                price = shp.to_buy[item]
                break

        if price is None:
            await interaction.followup.send(embed=discord.Embed(
                title="Can't buy that",
                description=f"That item isn't for sale! <:RuanMeiCurious:1173930315195101234> Check shops with `/critter shops`.",
                colour=discord.Colour.red()
            ), ephemeral=True)
            return

        if item in data.Data.LEGACY_ITEMS:
            item_name = data.Data.LEGACY_ITEMS[item].name
        else:
            item_name = gatos.items_helper[item].DISPLAY_NAME

        if player.currency < price * amount:
            await interaction.followup.send(embed=discord.Embed(
                title="You're broke!!",
                description=f"You don't have enough {CURRENCY_EMOJI} {CURRENCY_NAME}s to buy {amount} {item_name}(s)! <a:RuanMeiBugcatBroke:1181134215446806579> Check your balance with `/critter balance`.",
                colour=discord.Colour.red()
            ), ephemeral=True)
            return

        player.currency -= price * amount
        description = await self.give_item_to_player(ctx, ctx.author, item, amount)
        await ctx.send(embed=discord.Embed(title="Item bought!", description=description, colour=discord.Colour.teal()))


    @app_commands.command(
        name="pullstatus",
        description="Debug command to see 50/50 and pities",
        auto_locale_strings=False
    )
    @init_nursery
    async def pullstatus(self, interaction: discord.Interaction, member: discord.Member = None):
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)

        if member is None:
            member = ctx.author

        if member.id in self.players:
            player = self.players[member.id]
            banner_per_tag = {b.tag: b for b in data.Data.banners}
            available_tags = [tag for tag in player.pulls_status.pities if tag in banner_per_tag.keys()]
            embed = discord.Embed(title=f"{member.display_name}'s pulls status", colour=discord.Colour.teal())
            for tag in available_tags:
                description = ""
                for r in player.pulls_status.pities[tag]:
                    description += f"{r}:star: pity: {player.pulls_status.pities[tag][r]}/{banner_per_tag[tag].pities[int(r)]}\n"
                if tag in player.pulls_status.fiftyfifties:
                    for r in player.pulls_status.fiftyfifties[tag]:
                        description += f"{r}:star: on 50/50 : "
                        description += "Yes\n" if player.pulls_status.fiftyfifties[tag][r] else "No\n"
                embed.add_field(
                    name=tag.capitalize(),
                    value=description
                )
            await ctx.send(embed=embed)
        else:
            await ctx.send(content="❌ This player isn't in our records")


    async def on_error(self, interaction: discord.Interaction, error: app_commands.CommandInvokeError):
        try:
            await interaction.response.defer()
        except:
            # Already defered
            pass
        if isinstance(error, discord.app_commands.MissingAnyRole):
            await interaction.followup.send("You don't have the permission to use that command <:RuanMeiGun:1196842753347309608>")
        else:
            await interaction.followup.send("An error happened and bot devs may or may not try to understand what happened <a:RuanMeiAiPeace:1164689665740259369>")
            err = ''.join(traceback.TracebackException.from_exception(error).format())
            try:
                chan = self.bot.get_channel(1148381402111426693)
                await chan.send(f"Gato game error ```{err}```")
            except:
                print(err, file=sys.stderr)



async def setup(bot: commands.Bot):
    await bot.add_cog(GatoGame(bot))
    synced = await bot.tree.sync()
    gc = 0
    for guild in bot.guilds:
        await bot.tree.sync(guild=guild)
        gc += 1
    print(f"Synced {len(synced)} command(s) on {gc} guilds.")
