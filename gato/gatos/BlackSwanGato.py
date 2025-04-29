# from random import random
import random
from ABaseGato import ABaseGato, require_alive

class BlackswanGato(ABaseGato):
    """
        > Fav Food: Chocolate
        > Upon deployment draw one tarot card.
            Every 10 minutes there is a 50/50 chance to increase/decrease a random stat
            (among hp, hunger, energy, mood or efficiency) by 10%
            (efficiency boost/decrease only lasts for 10 minutes).
        > Eidolons: e1->e5 (boost increases up to 15%, 1% every eidolon)
        > E6: (Increases 50/50 chance to 70/30)
    """

    # Override constants
    IMAGE = "https://ibb.co/pz6B903"
    ANIMATIONS = "blackswangato"
    DISPLAY_NAME = "Blackberry Mousse"
    RARITY = 4
    VALUES_TO_SAVE = ABaseGato.VALUES_TO_SAVE + [
        "buff_cooldown",
        "buff_chance",
        "buff_percentage",
        "random_stats",
        "og_efficiency"
    ]

    # Override superclass values for stats

    # Custom variables used for this gato
    buff_cooldown: int = 0              # Remaining cooldown until its buff can be triggered again
    buff_chance: int = 0.5              # Chance for buff to increase or decrease
    buff_percentage: int = 0.1          # Percent that buff will be applied
    og_efficiency: float = None         # Value that keeps track of original efficiency
    BUFF_KEY: str = "BSG_eff_buff"      # dict key to keep track of this gato's buffs
    random_stats: list = ["health", "energy", "hunger", "efficiency", "mood"]

    # Helper to pick pos/neg sign representing incr/decr 
    def incr_decr_sign(self, chance):
        choices = [True, False]
        weights = [chance, 1-chance]
        pick = random.choices(choices, weights=weights, k=1)[0]
        return 1.0 if pick else -1.0

    @require_alive
    def random_buff(self, seconds):
        # Set percentage and chance according to eidolon
        if self.eidolon > 0:
            buff_percentage = min(0.15, 0.1+ self.eidolon*0.01)
        if self.eidolon > 6:
            self.buff_chance = 0.7

        self.buff_cooldown -= seconds
        if self.buff_cooldown <= 0:
            # Reset efficiency
            if self.og_efficiency is not None:
                self.efficiency = self.og_efficiency
            
            # Calculate increase or decrease
            chosen_percentage = 1.0 + (self.incr_decr_sign(self.buff_chance) * self.buff_percentage)
            
            # Decide random stat
            chosen_stat = random.choice(self.random_stats)
           
            # Save original efficiency
            self.og_efficiency = self.efficiency

            # Set chosen_stat with chosen_percentage
            setattr(self, chosen_stat, getattr(self, chosen_stat) * chosen_percentage)

            # 10 min CD
            self.buff_cooldown = 10*60


    def simulate(self, team: list["ABaseGato"], seconds: int = 1):
        # We calculate its efficiency boost before its actions
        self.random_buff(seconds)

        # Then call the parent simulation (VERY IMPORTANT)
        super().simulate(seconds)

