import time
from functools import wraps
from random import random

from ABaseGato import ABaseGato


def skelly_require_alive(function):
    """Decorator that only executes a function if the gato has not fainted. **Warning:** Don't add that to functions that shouldn't return `None`."""
    @wraps(function)
    def new_function(gato: "ABaseGato", *args, **kwargs):
        if gato.health > 0:
            return function(gato, *args, **kwargs)

    return new_function


class SkellyGato(ABaseGato):
    # Kit parameters
    HP_ON_REVIVE: int = 50
    RUSH_HOUR_DURATION_MINUTES: int = 20
    RUSH_HOUR_CD_MINUTES: int = 120
    RUSH_HOUR_STAT_RECOVERY: int = 30
    RUSH_HOUR_EFFICIENCY_BUFF: int = 100
    RUSH_HOUR_DURATION_PER_EIDOLON: int = 2
    RUSH_HOUR_CD_PER_EIDOLON: int = 6

    IMAGE = "https://i.ibb.co/nRgKgjz/skellygato.png"
    ANIMATIONS = "skellygato"
    DISPLAY_NAME = "Cotton Candy"
    RARITY = 5
    VALUES_TO_SAVE = ABaseGato.VALUES_TO_SAVE + [
        "rush_hour_trigger_date"
    ]

    SKELLY_RUSH_HOUR_EVENT_TYPE = "skelly_rush_hour"
    SKELLY_DIED_EVENT_TYPE = "skelly_died"
    EVENT_DESCRIPTIONS = ABaseGato.EVENT_DESCRIPTIONS | {
        SKELLY_RUSH_HOUR_EVENT_TYPE: "entered Rush Hour state! (x{count})",
        SKELLY_DIED_EVENT_TYPE: "fainted. **You won't need a Defibrilator** to revive it."
    }

    # Kit description
    __doc__ = f"""
        > When HP reaches 0, revives with {HP_ON_REVIVE} HP and enters Rush Hour state for {RUSH_HOUR_DURATION_MINUTES} minutes. This effect can be triggered once every {RUSH_HOUR_CD_MINUTES//60} hours.
        > When entering Rush Hour state, restores {RUSH_HOUR_STAT_RECOVERY} mood and energy.
        > During Rush Hour state, increases chance to find rare objects and boosts efficiency by {RUSH_HOUR_EFFICIENCY_BUFF}%. Guaranteed to find at least one rare item during this state.
        > If {DISPLAY_NAME} dies, it will not need a Defibrilator to revive, you can directly heal it.
        > Eidolons: E1 -> E5: increases Rush Hour state duration by {RUSH_HOUR_DURATION_PER_EIDOLON} minutes and decreases its CD by {RUSH_HOUR_CD_PER_EIDOLON} for each eidolon.
        > E6: Upon deployment, automatically trigger Rush Hour state if it's not on CD.
    """

    # Custom variables used for this gato
    RUSH_HOUR_EFF_BUFF_KEY: str = "SG_rush_hour"    # dict key to keep track of this gato's stats reduction
    rush_hour_trigger_date: float = 0               # when rush hour was triggered for the last time


    def rush_hour_active(self) -> bool:
        current_ts = time.time()
        rh_duration = self.RUSH_HOUR_DURATION_MINUTES + self.RUSH_HOUR_DURATION_PER_EIDOLON * self.eidolon
        minutes_since_trigger = (current_ts - self.rush_hour_trigger_date) / 60
        return minutes_since_trigger < rh_duration

    def rush_hour_on_cd(self) -> bool:
        current_ts = time.time()
        rh_cd = self.RUSH_HOUR_CD_MINUTES - self.RUSH_HOUR_CD_PER_EIDOLON * self.eidolon
        minutes_since_trigger = (current_ts - self.rush_hour_trigger_date) / 60
        return minutes_since_trigger < rh_cd

    def rush_hour(self):
        self._events.append({self.SKELLY_RUSH_HOUR_EVENT_TYPE: None})
        self.rush_hour_trigger_date = time.time()
        self.add_health(self.HP_ON_REVIVE, allow_overflow=True)
        self.add_hunger(self.RUSH_HOUR_STAT_RECOVERY, allow_overflow=True)
        self.add_energy(self.RUSH_HOUR_STAT_RECOVERY, allow_overflow=True)
        self.add_mood(self.RUSH_HOUR_STAT_RECOVERY, allow_overflow=True)
        self.luck = 10.0
        self.efficiency_boosts[self.RUSH_HOUR_EFF_BUFF_KEY] = self.RUSH_HOUR_EFFICIENCY_BUFF / 100

        # Guaranteed to find a rare object
        self.fetched_objects += [self.find_object()]

    def end_rush_hour(self):
        if self.RUSH_HOUR_EFF_BUFF_KEY in self.efficiency_boosts:
            self.efficiency_boosts.pop(self.RUSH_HOUR_EFF_BUFF_KEY)
        self.luck = 1.0


    def deploy(self, team: list["ABaseGato"]):
        """Increase self hunger and energy on deploy"""
        if not self.rush_hour_active():
            self.end_rush_hour()
        if self.eidolon >= 6 and not self.rush_hour_on_cd():
            self.rush_hour()

    def add_health(self, amount: float, allow_overflow: bool = False):
        if amount < 0:
            amount = amount * max(0, 1 - sum(self.damage_reductions.values()))

        self.health += amount

        if self.health > self.max_health and not allow_overflow:
            self.health = self.max_health
        elif self.health <= 0.0:
            self.health = 0.0
            if not self.rush_hour_on_cd():
                # Trigger Rush Hour state
                self.rush_hour()
            else:
                # No need for a Defibrilator to revive
                self._fainted = False
                self._events.append({self.SKELLY_DIED_EVENT_TYPE: None})

    @skelly_require_alive
    def simulate(self, team: list["ABaseGato"], seconds: int = 1):
        # Check for end of Rush Hour
        if self.RUSH_HOUR_EFF_BUFF_KEY in self.efficiency_boosts and not self.rush_hour_active():
            self.end_rush_hour()

        # Then call the parent simulation (VERY IMPORTANT)
        super().simulate(team, seconds)
