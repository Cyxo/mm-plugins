from random import random

from ABaseGato import ABaseGato, require_alive

class LuochaGato(ABaseGato):
    """
    > Fav Food: Coffee
	> Restores an ally’s health by 12 when it reaches 30% of max HP.
	> (cooldown of 30 minutes)
	> Eidolons: e1->e4 (increases amount restored by 2)
	> E5: (increases threshold to 40%)
	> E6: (decreases cooldown to 25 minutes)
    """

    # Override constants
    IMAGE = "https://ibb.co/RPqFq6g"
    # IMAGE = "https://media.discordapp.net/attachments/1117346551644295239/1202027480735830136/luochagato.png"
    ANIMATIONS = "4star"
    DISPLAY_NAME = "Latte Macchiato"
    RARITY = 4
    VALUES_TO_SAVE = ABaseGato.VALUES_TO_SAVE + [
        "health_cooldown",
        "health_threshold",
        "health_restore"
    ]

    # Override superclass values for stats

    # Custom variables used for this gato 
    health_cooldown: int = 0                # 30 minutes default, set in heal_ally
    health_threshold: float = 0.3             # default to heal at <= 30%
    health_amount: int = 12                 # default 12, 2 per e, cap at 20
    chosen_ally: ABaseGato = None
    BUFF_KEY: str = "LCG_energy_buff"       # dict key to keep track of this gato's buffs

    # If there is Luocha event
    # LUOCHA_EVENT_TYPE = "luocha_event"
    # EVENT_DESCRIPTIONS = ABaseGato.EVENT_DESCRIPTIONS | {}

    @require_alive
    def heal_ally(self, seconds, team):
        # e1->e4 increase heal_amount by 2
        if self.eidolon >= 1:
            self.heal_amount = min(20, 12 + self.eidolon*2)
        
        # e5 increase health_threshold to 40%
        if self.eidolon >= 5:
            self.health_threshold = 0.4     

        # pick ally to heal
        if self.chosen_ally != None:
            for i in team:
                if i.health <= i.max_health * self.health_threshold:
                    self.chosen_ally = i

        self.health_cooldown -= seconds

        if self.health_cooldown <= 0 and self.chosen_ally != None:
            self.chosen_ally.add_health(self.health_amount)
            # e6 eidolon health cooldown to 25 mins
            if self.eidolon == 6:
                self.health_cooldown = 25*60
            else:
                self.health_cooldown = 30*60
            self.chosen_ally = None

    def simulate(self, team: list["ABaseGato"], seconds: int = 1):
        # We calculate its energy boost before its actions
        self.heal_ally(seconds, team)

        # Then call the parent simulation (VERY IMPORTANT)
        currency, objects = super().simulate(seconds)

        # Return gathered currency and objects
        return currency, objects
