from discord.utils import find

from AGatoConsumable import AGatoConsumable


class MedkitConsumable(AGatoConsumable):
    """> Restores 50 HP to the selected critter"""

    IMAGE: str = "https://i.ibb.co/3BTtqDg/Item-Healing-Spray.png"
    ANIMATIONS: str = "medkit"
    DISPLAY_NAME: str = "Healing Spray"
    RARITY: int = 3

    async def modal_callback(self, value):
        if value:
            gato = find(
                lambda g: g.DISPLAY_NAME == value,
                self._player.nursery
            )
            gato.add_health(50)

        await super().modal_callback(value)
