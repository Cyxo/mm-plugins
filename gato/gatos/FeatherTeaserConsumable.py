from discord.utils import find

from AGatoConsumable import AGatoConsumable


class FeatherTeaserConsumable(AGatoConsumable):
    """> Play with the critter to increase its mood by 50"""

    # IMAGE: str = "UPLOAD IT TO IMGBB.COM"
    # ANIMATIONS: str = "medkit"
    DISPLAY_NAME: str = "Feather teaser"
    RARITY: int = 3

    async def modal_callback(self, value):
        if value:
            gato = find(
                lambda g: g.DISPLAY_NAME == value,
                self._player.nursery
            )
            gato.add_mood(50)

        await super().modal_callback(value)
