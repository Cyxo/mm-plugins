from ABaseGato import ABaseGato, require_alive


class BladeGato(ABaseGato):
    """
        > Fav Food: Spider Lily
        > Every time HP decreases, increases all other stats by 20% the decreased amount. Every time HP increases, decreases all other stats by 20% the increased amount.
        > Eidolons: e1->e6 increases by 3 each. (20% at E0, 38% at E6)
        > E6: increase max hp by 20
    """

    IMAGE: str = "https://i.ibb.co/JtcFtmW/image.png"
    ANIMATIONS: str = "bladegato"
    DISPLAY_NAME: str = "Sesame Cake"
    RARITY: int = 4

    BLADE_HP_UP_EVENT_TYPE: str = "blade_hp_up"
    BLADE_HP_DOWN_EVENT_TYPE: str = "blade_hp_down"
    EVENT_DESCRIPTIONS: dict[str, str] = ABaseGato.EVENT_DESCRIPTIONS | {
        BLADE_HP_UP_EVENT_TYPE: "gained hp, other stats decreased! (x{count})",
        BLADE_HP_DOWN_EVENT_TYPE: "lost hp, other stats increased! (x{count})",
    }
    BLADE_EFF_BOOST_KEY: str = "blade_eff_boost"

    def hellscape(self, hp_delta: float):
        """Increases/decreses other stats as hp decreases/increases"""

        # stat changes
        multipler = 0.2 + self.eidolon * 0.03
        self.add_energy(-hp_delta * multipler)
        self.add_hunger(-hp_delta * multipler)
        self.add_mood(-hp_delta * multipler)
        self.efficiency_boosts[self.BLADE_EFF_BOOST_KEY] = self.efficiency_boosts.get(
            self.BLADE_EFF_BOOST_KEY, 0) + -hp_delta * multipler / 100

        # trigger event
        event_type = self.BLADE_HP_UP_EVENT_TYPE if hp_delta > 0 else self.BLADE_HP_DOWN_EVENT_TYPE
        self._events.append({event_type: None})

    @require_alive
    def add_health(self, amount: float, allow_overflow: bool = False):
        """Overrides base method to allow :py:meth:`hellscape` on health change"""

        super().add_health(amount, allow_overflow)
        self.hellscape(amount)

    def set_eidolon(self, value: int):
        """Override max health on e6"""

        super().set_eidolon(value)
        if self.eidolon == 6:
            self.max_health = 120
            super().add_health(20)

    def simulate(self, team: list["ABaseGato"], seconds: int = 1):
        """Delegates to base method"""

        super().simulate(team, seconds)
