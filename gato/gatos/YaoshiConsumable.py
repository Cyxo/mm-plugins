import discord
from discord.utils import find

from AGatoConsumable import AGatoConsumable


class YaoshiConsumable(AGatoConsumable):
    """> Replenish your critter's stats"""

    IMAGE: str = "https://i.ibb.co/RjWM61G/tl.png"
    ANIMATIONS: str = "yaoshisapple"
    DISPLAY_NAME: str = "Yaoshi's Apple"
    RARITY: int = 6

    async def modal_callback(self, value):
        if value:
            gato = find(
                lambda g: g.DISPLAY_NAME == value,
                self._player.nursery
            )

            gato._fainted = False
            gato.add_health(gato.max_health)
            gato.add_hunger(gato.max_hunger)
            gato.add_mood(gato.max_mood)
            gato.add_energy(gato.max_energy)

        await super().modal_callback(value)
