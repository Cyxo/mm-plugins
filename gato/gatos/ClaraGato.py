from ABaseGato import ABaseGato, require_alive


class ClaraGato(ABaseGato):
    """
        > Fav Food: Ice Cream
        > Reduces health decrease by 20%. Every time HP decreases, 
        > increase efficiency by 20% of the decreased amount. 
        > Every time HP increases, decreases efficiency by 20% of 
        > the increased amount.
        > Eidolons: e1->e5 (increases efficiency boost by 2%)
        > E6: (decreases health decrease by 30%)
    """

    # TODO: img & animation
    IMAGE: str = "https://i.ibb.co/zr82fFH/nuxiom-gato.png"
    # ANIMATIONS: str = "claragato"
    DISPLAY_NAME: str = "Pure Sugar Child"
    RARITY: int = 4

    CLARA_PROTECT_EVENT_TYPE: str = "clara_protection_of_svarog"
    CLARA_COUNTER_EVENT_TYPE: str = "clara_svarogs_counter"
    EVENT_DESCRIPTIONS: dict[str, str] = ABaseGato.EVENT_DESCRIPTIONS | {
        CLARA_PROTECT_EVENT_TYPE: "Under the protection of Svarog, DMG taken is reduced.",
        CLARA_COUNTER_EVENT_TYPE: "hp changed and Svarog countered! (x{count})",
    }
    CLARA_DMG_REDUCTION_KEY: str = "clara_dmg_reduction"
    CLARA_EFF_BOOST_KEY: str = "clara_eff_boost"

    def counter(self, hp_delta: float):
        """Increases/decreses efficiency boosts as health decreases/increases"""

        # update efficiency boost
        multipler = 0.2 + min(self.eidolon, 5) * 0.02
        self.efficiency_boosts[self.CLARA_EFF_BOOST_KEY] = self.efficiency_boosts.get(
            self.CLARA_EFF_BOOST_KEY, 0) + -hp_delta * multipler / 100

        # trigger event
        self._events.append({self.CLARA_COUNTER_EVENT_TYPE: None})

    @require_alive
    def add_health(self, amount: float, allow_overflow: bool = False):
        """Overrides base method to allow :py:meth:`counter` on health change"""

        super().add_health(amount, allow_overflow)
        self.counter(amount)

    def deploy(self, team: list["ABaseGato"]):
        """Overrides base method to apply damage reduction to self"""

        # Deploy base class first to reset modifiers
        super().deploy(team)

        # Apply damage reduction to self
        self.damage_reductions[self.CLARA_DMG_REDUCTION_KEY] = 0.2 if self.eidolon < 6 else 0.3

        # Send event
        self._events.append({self.CLARA_PROTECT_EVENT_TYPE: None})

    def simulate(self, team: list["ABaseGato"], seconds: int = 1):
        """Delegates to base method"""

        super().simulate(team, seconds)
