from discord.utils import find

from AGatoConsumable import AGatoConsumable, check_requirements


class FeatherTeaserConsumable(AGatoConsumable):
    """> Play with the critter to increase its mood by 50"""

    IMAGE: str = "https://i.ibb.co/HdbHftQ/tl.png"
    ANIMATIONS: str = "featherteaser"
    DISPLAY_NAME: str = "Feather teaser"
    RARITY: int = 3

    @check_requirements
    async def modal_callback(self, value, interaction):
        if value:
            gato = find(
                lambda g: g.DISPLAY_NAME == value,
                self._player.nursery
            )
            gato.add_mood(50)

        await super().modal_callback(value, interaction)
