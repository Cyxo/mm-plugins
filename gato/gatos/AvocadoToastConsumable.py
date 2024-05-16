from discord.utils import find

from AGatoConsumable import AGatoConsumable


class AvocadoToastConsumable(AGatoConsumable):
    """> Restores 30 hunger and 30 HP"""

    IMAGE: str = "https://i.ibb.co/y59Lmhh/tl.png"
    ANIMATIONS: str = "avocadotoast"
    DISPLAY_NAME: str = "Avocado toast"
    RARITY: int = 3

    async def modal_callback(self, value):
        if value:
            gato = find(
                lambda g: g.DISPLAY_NAME == value,
                self._player.nursery
            )
            gato.add_health(30)
            gato.add_hunger(30)

        await super().modal_callback(value)
