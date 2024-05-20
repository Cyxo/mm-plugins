from discord.utils import find

from AGatoConsumable import AGatoConsumable, check_requirements


class SalmonConsumable(AGatoConsumable):
    """> Restores 50 hunger"""

    IMAGE: str = "https://i.ibb.co/q1zB1k2/tl.png"
    ANIMATIONS: str = "salmon"
    DISPLAY_NAME: str = "Salmon"
    RARITY: int = 3

    @check_requirements
    async def modal_callback(self, value, interaction):
        if value:
            gato = find(
                lambda g: g.DISPLAY_NAME == value,
                self._player.nursery
            )
            gato.add_hunger(50)

        await super().modal_callback(value, interaction)
