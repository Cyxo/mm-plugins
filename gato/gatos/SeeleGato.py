from random import random

from ABaseGato import ABaseGato, require_alive

class SeeleGato(ABaseGato):
    """
        > Fav food: Monster.
        > Everytime a total amount of 200 (150 at E6) currency has been gained, increases efficiency by 15% for 5 minutes.
        > Each Eidolon between E1-E5 further boosts efficiency by 1% for 5 minutes.
    """

    # Override constants
    IMAGE = "https://i.ibb.co/0QJhz0c/seelegato.png"
    ANIMATIONS = "seelegato"
    DISPLAY_NAME = "Berry Butterfly"
    RARITY = 4
    VALUES_TO_SAVE = ABaseGato.VALUES_TO_SAVE + [
        "buff_duration",
        "currency_fetched"
    ]
    SEELE_EVENT_KEY = "seele_its_my_turn"
    EVENT_DESCRIPTIONS = ABaseGato.EVENT_DESCRIPTIONS | {
        SEELE_EVENT_KEY: "took one more turn and got an efficiency buff! (x{count})"
    }

    # Custom variables used for this gato
    buff_duration: int = 0              # Remaining duration for its buff
    SEELE_BUFF_KEY: str = "SG_eff_buff" # dict key to keep track of this gato's buffs
    currency_fetched: float = 0         # To keep track of how much currency the gato fetched since last buff


    @require_alive
    def efficiency_buff(self, seconds):
        # Update buff duration
        if self.SEELE_BUFF_KEY in self.efficiency_boosts:
            self.buff_duration -= seconds

        CURRENCY_THRESHOLD = 20
        if self.eidolon >= 6:
            CURRENCY_THRESHOLD = 15

        # Apply buff if cooldown is over
        if (self.currency_fetched > CURRENCY_THRESHOLD or self.buff_duration > 0) and not self.SEELE_BUFF_KEY in self.efficiency_boosts:
            # Reset currency fetched
            self.currency_fetched = 0

            # Increase efficiency boost
            self.efficiency_boosts[self.SEELE_BUFF_KEY] = 15/100 + (1/100 * min(self.eidolon, 5))

            # Set base cooldown and duration
            self.buff_duration += 5*60

            self._events.append({self.SEELE_EVENT_KEY: None})

        # Remove buff if duration is over
        if self.buff_duration <= 0 and self.SEELE_BUFF_KEY in self.efficiency_boosts:
            self.efficiency_boosts.pop(self.SEELE_BUFF_KEY)


    def compute_currency(self, seconds):
        currency = super().compute_currency(seconds)
        self.currency_fetched += currency
        return currency


    def simulate(self, team: list["ABaseGato"], seconds: int = 1):
        # We calculate its efficiency boost before its actions
        self.efficiency_buff(seconds)

        # Then call the parent simulation (VERY IMPORTANT)
        super().simulate(team, seconds)
