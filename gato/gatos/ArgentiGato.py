from random import random

from ABaseGato import ABaseGato, require_alive

class ArgentiGato(ABaseGato):
    """
        > Fav Food: Quaso
        > For every 5 energy over 60, increases efficiency by 5%.
        > (can only stack up to 4 times)
        > Eidolons: e1->e5 (decreases needed energy from
        > 60 to 40, 4 per eidolon)
        > E6: (boosts base energy from 100 to 110 and increases stacks up to 5)
    """

    # Override constants
    IMAGE = "https://i.ibb.co/8cfy5W5/argenti-gato.png"
    # ANIMATIONS = "4star"
    DISPLAY_NAME = "Creme de Rose"
    RARITY = 4
    VALUES_TO_SAVE = ABaseGato.VALUES_TO_SAVE + [
        "energy_threshold",
        "max_stacks"
    ]

    # Override superclass values for stats

    # Custom variables used for this gato
    energy_threshold: int = 60          # Energy threshold to count towards efficiency buff
    max_stacks: int = 4                 # Max stacks of 5% allowed
    BUFF_KEY: str = "BCG_buff"          # dict key to keep track of this gato's buffs

    # If we have Argenti event
    # ARGENTI_EVENT_TYPE = "bs_event"
    # EVENT_DESCRIPTIONS = ABaseGato.EVENT_DESCRIPTIONS | {}

    @require_alive
    def efficiency_buff(self, seconds):
        if self.eidolon == 6:
            self.max_energy = 110
            self.max_stacks = 5
        if self.eidolon >= 1:
            self.energy_threshold = max(40, 60 - self.eidolon*4) # decreases energy_threshold by 4 per e, cap at 40

        diff_energy = self.energy - self.energy_threshold
        if diff_energy > 0:
            curr_stack = min(diff_energy // 5, self.max_stacks)
            self.efficiency = self.efficiency*(1.0+(0.5*curr_stack))

    def simulate(self, team: list["ABaseGato"], seconds: int = 1):
        # We calculate its energy boost before its actions
        self.efficiency_buff(seconds)

        # Then call the parent simulation (VERY IMPORTANT)
        super().simulate(team, seconds)
