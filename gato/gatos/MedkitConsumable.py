from discord.utils import find

from AGatoConsumable import AGatoConsumable


class MedkitConsumable(AGatoConsumable):
    """> Restores 50 HP to the selected critter"""

    # TODO: ask swede for the image and upload to imgbb.com
    IMAGE: str = "https://i.ibb.co/9n5gT9D/download.png"
    ANIMATIONS: str = "medkit"
    DISPLAY_NAME: str = "Medkit"
    RARITY: int = 3

    async def modal_callback(self, value):
        if value:
            gato = find(
                lambda g: g.DISPLAY_NAME == value,
                self._player.nursery
            )
            gato.add_health(50)

        await super().modal_callback(value)
