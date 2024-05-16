from discord.utils import find

from AGatoConsumable import AGatoConsumable


class CatTreatsConsumable(AGatoConsumable):
    """> Restores 30 hunger and 50 energy"""

    # IMAGE: str = "UPLOAD IT TO IMGBB.COM"
    # ANIMATIONS: str = "medkit"
    DISPLAY_NAME: str = "Cat treats"
    RARITY: int = 3

    async def modal_callback(self, value):
        if value:
            gato = find(
                lambda g: g.DISPLAY_NAME == value,
                self._player.nursery
            )
            gato.add_energy(50)

        await super().modal_callback(value)
