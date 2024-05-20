import asyncio
from functools import wraps

import discord
from discord.utils import find

from discord.ext.commands.context import Context

from AConsumable import AConsumable
from ViewGato import ViewGato


def check_requirements(function):
    """Decorator that only executes a function if the gato has not fainted. **Warning:** Don't add that to functions that shouldn't return `None`."""
    @wraps(function)
    async def new_function(cons: "AGatoConsumable", value, interaction: discord.Interaction, *args, **kwargs):
        if value:
            gato = find(
                lambda g: g.DISPLAY_NAME == value,
                cons._player.nursery
            )
            if cons.REQUIRE_ALIVE and gato._fainted and value != "Cotton Candy":
                embed = discord.Embed(
                    title=f"Failed to use {cons.DISPLAY_NAME}",
                    description="This critter has fainted. Use a **Defibrilator** to revive it first.",
                    color=discord.Colour.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return await function(cons, None, interaction, *args, **kwargs)
            elif cons.REQUIRE_UNDEPLOYED and cons._player.deployed_team is not None and \
                gato in cons._player.deployed_team.gatos and cons._player.deployed_team.deployed_at is not None:
                embed = discord.Embed(
                    title=f"Failed to use {cons.DISPLAY_NAME}",
                    description="This critter is still deployed! Use `/critter recall` first.",
                    color=discord.Colour.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return await function(cons, None, interaction, *args, **kwargs)
            else:
                return await function(cons, value, interaction, *args, **kwargs)

    return new_function


class AGatoConsumable(AConsumable):
    """Abstract class for consumables where you have to select a Gato"""

    REQUIRE_ALIVE = True
    REQUIRE_UNDEPLOYED = True

    _player = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.result = None

    async def modal_callback(self, value, interaction):
        # Override it
        if value:
            self.result = True
        else:
            self.result = False

    async def consume(self, ctx: Context, gatogame):
        await super().consume(ctx, gatogame)

        self._player = gatogame.players[ctx.author.id]
        count = self._player.inventory[self.__class__.__name__]

        view = ViewGato(
            player=self._player,
            callback=self.modal_callback
        )

        message = await ctx.send(
            content=f"You have **{count} {self.DISPLAY_NAME}** left. Which critter do you want to use **{self.DISPLAY_NAME}** on?",
            view=view,
            ephemeral=True
        )

        while self.result is None:
            await asyncio.sleep(0.5)

        await message.delete()

        return self.result
