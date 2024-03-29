import traceback

import discord
from discord.ext import commands

from discord import Interaction, SelectOption
from discord.ui import View, Select, Button, select, button
from discord.utils import MISSING


class ViewGato(View):

    @select(placeholder="Select a critter to use this on")
    async def gato(self, interaction: Interaction, select: Select):
        await interaction.response.defer()
        await self.callback(select.values[0])
        await self.stop()

    @button(style=discord.ButtonStyle.red, label="Cancel")
    async def cancel(self, interaction: Interaction, button: Button):
        await interaction.response.defer()
        await self.callback(None)
        await self.stop()

    def __init__(self, player, callback) -> None:
        super().__init__()
        for g in player.nursery:
            self.gato.add_option(
                label=g.name,
                description=f"{g.health} ❤️ | {g.hunger} 🍗 | {g.energy} ⚡ | {g.mood} 🌞",
                value=g.DISPLAY_NAME
            )
        self.callback = callback

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.defer()
        await self.callback(None)
        traceback.print_exception(type(error), error, error.__traceback__)
        await self.stop()

    async def on_timeout(self) -> None:
        await self.callback(None)
        await self.stop()

