from discord.utils import find

from AGatoConsumable import AGatoConsumable
from EfficiencyFoodEq import EfficiencyFoodEq
from SwedeGato import SwedeGato


class SwedishFishConsumable(AGatoConsumable):
    """> Restores 30 hunger and increases efficiency by 10% for 1 hour. ⚠️ Efficiency food buffs don't stack!"""

    IMAGE: str = "https://i.ibb.co/McD71pV/image0.png"
    ANIMATIONS: str = "swedishfish"
    DISPLAY_NAME: str = "Swedish Fish"
    RARITY: int = 3

    async def modal_callback(self, value):
        if value:
            gato = find(
                lambda g: g.DISPLAY_NAME == value,
                self._player.nursery
            )
            idx = None
            for i, eq in enumerate(gato.equipments):
                if eq.DISPLAY_NAME == EfficiencyFoodEq.DISPLAY_NAME:
                    idx = i

            if idx is not None:
                gato.equipments.pop(idx)

            gato.add_hunger(30)
            gato.equipments.append(EfficiencyFoodEq())

            # Handle favorite food
            if gato.DISPLAY_NAME == SwedeGato.DISPLAY_NAME:
                gato.add_mood(20)
                gato.add_hunger(20)

        await super().modal_callback(value)
