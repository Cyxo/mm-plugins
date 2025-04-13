from ABaseGato import ABaseGato, require_alive


class LynnGato(ABaseGato):
    # Kit parameters
    ALLIES_HP_BUFF_AMOUNT: int = 20
    HP_DECREASE_TIMEFRAME_MINS: int = 30
    HP_DECREASE_AMOUNT: int = 5
    EFF_BOOST_PERCENTAGE: int = 15
    EFF_BOOST_PERCENTAGE_PER_EIDOLON: int = 2
    ALLIES_BITE_CHANCE_REDUCTION_PERCENTAGE: int = 40
    E6_ADDITIONAL_BITE_CHANCE_REDUCTION_PERCENTAGE: int = 40

    # Kit description
    __doc__ = f"""
        > Fav Food:
        > While deployed, increase all allies health by {ALLIES_HP_BUFF_AMOUNT}. 
        > Lynn’s health doesn’t deplete, instead every {HP_DECREASE_TIMEFRAME_MINS} minutes Lynn consumes {HP_DECREASE_AMOUNT} health (health doesn’t decrease past 1) 
        > she increases efficiency by {EFF_BOOST_PERCENTAGE}% and lowers allies base chance to attack the owner/gatos by {ALLIES_BITE_CHANCE_REDUCTION_PERCENTAGE}%.
        > Eidolons: e1 -> e5: efficency increases for an additional {EFF_BOOST_PERCENTAGE_PER_EIDOLON}% for each eidolon.
        > e6: lowers allies base chance to attack the owner/gatos by an additional {E6_ADDITIONAL_BITE_CHANCE_REDUCTION_PERCENTAGE}%.
    """

    IMAGE = "https://cdn.discordapp.com/attachments/1198010808672723075/1211136378469875712/lynn_gato.png"
    # ANIMATIONS = "lynngato"
    DISPLAY_NAME = "Red Velvet"
    RARITY = 5
    VALUES_TO_SAVE = ABaseGato.VALUES_TO_SAVE + [
        "hp_loss_cooldown",
    ]

    LYNN_STATS_UP_EVENT_TYPE = "lynn_stats_up"
    EVENT_DESCRIPTIONS = ABaseGato.EVENT_DESCRIPTIONS | {
        LYNN_STATS_UP_EVENT_TYPE: "increased all allies' health and reduced their chance to attack the owner!",
    }
    BUFF_KEY = "lynn_buff_key"

    # Mutable state variables used for this gato
    hp_loss_cooldown: int = 0

    def maybe_lose_health(self, seconds: int):
        """Triggers hp loss at fixed time interval (see kit description) and never go below 1 hp."""

        # Tick down hp loss cd if needed
        if self.hp_loss_cooldown > 0:
            self.hp_loss_cooldown = max(self.hp_loss_cooldown - seconds, 0)

        # Lose hp if not in cooldown or at min hp
        if self.hp_loss_cooldown <= 0 and self.health > 1:
            loss_amount = min(self.HP_DECREASE_AMOUNT, self.health - 1)
            super().add_health(-loss_amount)
            self.hp_loss_cooldown = self.HP_DECREASE_TIMEFRAME_MINS * 60

    def deploy(self, team: list["ABaseGato"]):
        """Increase mood and energy for the team on deploy"""

        # Run base class deploy
        super().deploy(team)

        # Apply own efficiency boost
        self.efficiency_boosts[self.BUFF_KEY] = (
            self.EFF_BOOST_PERCENTAGE + min(self.eidolon, 5) * self.EFF_BOOST_PERCENTAGE_PER_EIDOLON) / 100

        # Apply team wide hp buff and bite chance reduction
        bite_chance_reduction = self.ALLIES_BITE_CHANCE_REDUCTION_PERCENTAGE / 100
        if self.eidolon >= 6:
            bite_chance_reduction += self.E6_ADDITIONAL_BITE_CHANCE_REDUCTION_PERCENTAGE / 100
        for g in team:
            g.add_health(self.ALLIES_HP_BUFF_AMOUNT, allow_overflow=True)
            g.bite_chance_reductions[self.BUFF_KEY] = bite_chance_reduction

        # Send event
        self._events.append({self.LYNN_STATS_UP_EVENT_TYPE: None})

    def add_health(self, amount: float, allow_overflow: bool = False):
        # Block normal health decreases
        if amount >= 0:
            super().add_health(amount, allow_overflow)

    def simulate(self, team: list["ABaseGato"], seconds: int = 1):
        # Apply specialised health decrease mechanic
        self.maybe_lose_health(seconds)

        # Then call the parent simulation (VERY IMPORTANT)
        super().simulate(team, seconds)
