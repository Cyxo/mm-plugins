from discord.utils import find

from AGatoConsumable import AGatoConsumable


class SalmonConsumable(AGatoConsumable):
    """> Restores 50 hunger"""

    # IMAGE: str = "UPLOAD IT TO IMGBB.COM"
    # ANIMATIONS: str = "medkit"
    DISPLAY_NAME: str = "Salmon"
    RARITY: int = 3

    async def modal_callback(self, value):
        if value:
            gato = find(
                lambda g: g.DISPLAY_NAME == value,
                self._player.nursery
            )
            gato.add_hunger(50)

        await super().modal_callback(value)
