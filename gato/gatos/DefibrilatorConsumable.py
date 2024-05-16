import discord
from discord.utils import find

from AGatoConsumable import AGatoConsumable


class DefibrilatorConsumable(AGatoConsumable):
    """> Revives an undeployed critter with 20 HP"""

    # IMAGE: str = "UPLOAD IT TO IMGBB.COM"
    # ANIMATIONS: str = "medkit"
    DISPLAY_NAME: str = "Defibrilator"
    RARITY: int = 3

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ctx = None
        self.team = None

    async def modal_callback(self, value):
        if value:
            gato = find(
                lambda g: g.DISPLAY_NAME == value,
                self._player.nursery
            )

            if self.tm is not None and self.tm.deployed_at is not None and gato in self.tm.gatos:
                embed = discord.Embed(
                    title = "Defibrilator",
                    description = f"**{gato.name}** is currently deployed. Please recall it using `/critter recall` first",
                    colour = discord.Colour.red()
                )
                await self.ctx.send(embed=embed, ephemeral=True)
                self.result = False
                return

            if not gato._fainted:
                embed = discord.Embed(
                    title = "Defibrilator",
                    description = f"**{gato.name}** has not fainted, so it can't be revived",
                    colour = discord.Colour.red()
                )
                await self.ctx.send(embed=embed, ephemeral=True)
                self.result = False
                return

            gato._fainted = False
            gato.add_health(20)

        await super().modal_callback(value)

    async def consume(self, ctx, gatogame):
        player = gatogame.players[ctx.author.id]

        self.tm = player.deployed_team
        self.ctx = ctx
        return await super().consume(ctx, gatogame)
