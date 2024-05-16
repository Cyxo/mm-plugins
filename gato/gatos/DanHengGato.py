
from ABaseGato import ABaseGato, require_alive

class DanHengGato(ABaseGato):
    """
        > Fav Food: Shumai
        >Every time energy decreases, increases all other stats by 10% the decreased amount. 
        >Every time energy increases, decreases all other stats by 10% of the increased amount. 
        >Eidolons: e1->e6 increases by 1.5 each. (10% at E0, 19% at E6)
        >E6: increase max energy by 20

    """

    # Override constants
    IMAGE = "https://i.ibb.co/KLzR779/danheng-gato.png"
    # ANIMATIONS = "4star"
    DISPLAY_NAME = "Rice Dumpling"
    RARITY = 4

    DHENG_ENERGY_UP_EVENT_TYPE: str = "DanHeng_energy_up"
    DHENG_ENERGY_DOWN_EVENT_TYPE: str = "DanHeng_energy_down"
    EVENT_DESCRIPTIONS: dict[str, str] = ABaseGato.EVENT_DESCRIPTIONS | {
        DHENG_ENERGY_UP_EVENT_TYPE: "gained energy, other stats decreased! (x{count})",
        DHENG_ENERGY_DOWN_EVENT_TYPE: "lost energy, other stats increased! (x{count})",
    }
    DHENG_EFF_BOOST_KEY: str = "DanHeng_eff_boost"

    def concentration(self, energy_delta: float):
        """Increases/decreses other stats as hp decreases/increases"""

        # stat changes
        multipler = 0.1 + self.eidolon * 0.015
        self.add_health(-energy_delta * multipler)
        self.add_hunger(-energy_delta * multipler)
        self.add_mood(-energy_delta * multipler)
        self.efficiency_boosts[self.DHENG_EFF_BOOST_KEY] = self.efficiency_boosts.get(
            self.DHENG_EFF_BOOST_KEY, 0) + -energy_delta * multipler / 100

        # trigger event
        event_type = self.DHENG_ENERGY_UP_EVENT_TYPE if energy_delta > 0 else self.DHENG_ENERGY_DOWN_EVENT_TYPE
        self._events.append({event_type: None})

    @require_alive
    def add_energy(self, amount: float):
        """Overrides base method to allow :py:meth:`concentration` on health change"""

        super().add_energy(amount)
        self.concentration(amount)

    def set_eidolon(self, value: int):
        """Override max health on e6"""

        super().set_eidolon(value)
        if self.eidolon == 6:
            self.max_energy = 120
            super().add_energy(20)

    def simulate(self, team: list["ABaseGato"], seconds: int = 1):
        """Delegates to base method"""
        
        super().simulate(team, seconds)

