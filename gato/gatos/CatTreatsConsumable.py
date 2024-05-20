from discord.utils import find

from AGatoConsumable import AGatoConsumable, check_requirements


class CatTreatsConsumable(AGatoConsumable):
    """> Restores 30 hunger and 50 energy"""

    IMAGE: str = "https://i.ibb.co/XsGLW67/tl.png"
    ANIMATIONS: str = "cattreats"
    DISPLAY_NAME: str = "Cat treats"
    RARITY: int = 3

    @check_requirements
    async def modal_callback(self, value, interaction):
        if value:
            gato = find(
                lambda g: g.DISPLAY_NAME == value,
                self._player.nursery
            )
            gato.add_energy(50)

        await super().modal_callback(value, interaction)
