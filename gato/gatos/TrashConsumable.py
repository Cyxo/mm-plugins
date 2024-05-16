from discord.utils import find

from AGatoConsumable import AGatoConsumable


class TrashConsumable(AGatoConsumable):
    """> Poison food. Reduces HP by 20, restores 50 hunger."""

    IMAGE: str = "https://i.ibb.co/7Rxqgzf/Item-Trash.png"
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
