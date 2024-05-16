from AEquipment import AEquipment
from ABaseItem import ItemType

class FakeMouseEq(AEquipment):
    """> Boosts efficiency by 15% for 1 hour"""

    ITEM_TYPE: ItemType = ItemType.EQUIPMENT
    DISPLAY_NAME = "Fake mouse"
    VALUES_TO_SAVE = AEquipment.VALUES_TO_SAVE + [
        "buff_duration"
    ]

    MOUSE_BUFF_KEY = "fake_mouse_eff_buff"

    buff_duration: int

    def __init__(self, **kwargs):
        self.buff_duration = 0
        super().__init__(**kwargs)

    def simulate(self, gato, seconds: int = 1):
        super().simulate(gato, seconds)

        if self.MOUSE_BUFF_KEY not in gato.efficiency_boosts:
            gato.efficiency_boosts[self.MOUSE_BUFF_KEY] = 0.15
            self.buff_duration = 3600
        else:
            if self.buff_duration > 0:
                self.buff_duration -= seconds
            else:
                gato.efficiency_boosts.pop(self.MOUSE_BUFF_KEY)
                self.used_up = True
