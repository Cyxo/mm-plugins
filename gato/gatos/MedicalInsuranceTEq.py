from AEquipment import AEquipment
from ABaseItem import ItemType

class MedicalInsuranceTEq(AEquipment):
    """> Upon claim, covers all expenses related to critter bites for the equipped team. Single use."""

    IMAGE = "https://i.ibb.co/xhSvxV0/tl.png"
    ANIMATIONS = "healthinsurance"
    ITEM_TYPE: ItemType = ItemType.TEAM_EQUIPMENT
    DISPLAY_NAME = "Health Insurance"
    RARITY = 4

    def claim(self, gato):
        super().claim(gato)

        self.used_up = True

    def simulate(self, gato, seconds: int = 1):
        super().simulate(gato, seconds)

        for evt in gato._events:
            k = list(evt.keys())[0]
            evt[k] = 0
