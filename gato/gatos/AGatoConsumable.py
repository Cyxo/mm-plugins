import asyncio

from discord.utils import find

from discord.ext.commands.context import Context

from AConsumable import AConsumable
from ViewGato import ViewGato


class AGatoConsumable(AConsumable):
    """Abstract class for consumables where you have to select a Gato"""

    _player = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.result = None

    async def modal_callback(self, value):
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
