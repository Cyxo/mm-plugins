from discord.utils import find

from AGatoConsumable import AGatoConsumable


class TrashConsumable(AGatoConsumable):
    """> Poison food. Reduces HP by 20, restores 50 hunger."""

    # TODO: take the HSR trash image from some wiki and upload to imgbb.com
    IMAGE: str = "https://i.ibb.co/9n5gT9D/download.png"
    ANIMATIONS: str = "trash"
    DISPLAY_NAME: str = "Trash"
    RARITY: int = 3

    async def modal_callback(self, value):
        if value:
            gato = find(
                lambda g: g.DISPLAY_NAME == value,
                self._player.nursery
            )
            gato.add_health(-20)
            gato.add_hunger(50)

        await super().modal_callback(value)
