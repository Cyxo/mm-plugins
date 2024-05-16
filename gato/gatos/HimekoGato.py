from random import random

from ABaseGato import ABaseGato, require_alive

class HimekoGato(ABaseGato):
    """
        > Fav Food: Coffee
        > Every 10 minutes gain 1 point of charge (max 3).
        > Once max points have been reached, recover 10 energy
        > for all allies. (goes on cooldown for 30 minutes)
        > Eidolon: e1-e5 (increases energy recovered to 20, 2 per eidolon)
        > E6: (increases charges gained upon deployment to 2)
    """

    # Override constants
    IMAGE = "https://i.ibb.co/LCpWG4P/himeko-gato1.png"
    # ANIMATIONS = "4star"
    DISPLAY_NAME = "Rose Tiramisu"
    RARITY = 4
    VALUES_TO_SAVE = ABaseGato.VALUES_TO_SAVE + [
        "himeko_charge",
        "charge_cooldown",
        "energy_cooldown",
        "energy_to_recover"
    ]

    # Override superclass values for stats

    # Custom variables used for this gato
    himeko_charge: int = 0              # Current points of charges (max 3)
    charge_cooldown: int = 10*60        # Remaining cooldown until gain 1 point of charge
    energy_cooldown: int = 0            # Remaining cooldown until its buff can be triggered again
    energy_to_recover: int = 10         # Energy to recover, default 10, incr to 20
    BUFF_KEY: str = "HG_energy_buff"       # dict key to keep track of this gato's buffs

    # If there is Himeko event
    # HIMEKO_EVENT_TYPE = "himeko_event"
    # EVENT_DESCRIPTIONS = ABaseGato.EVENT_DESCRIPTIONS | {}

    @require_alive
    def energy_buff(self, seconds, team):
        if self.eidolon == 6:
            if self._time_deployed == 0:
                self.himeko_charge += 1 # increases charges gained upon deployment to 2
        if self.eidolon >= 1:
            self.energy_to_recover = min(20, 10 + 2*self.eidolon) # increases energy recovered 2 per eidolon, cap at 20

        if self.energy_cooldown == 0:
            if self.charge_cooldown <= 0:
                self.himeko_charge += 1
                self.charge_cooldown = 10*60
            else:
                self.charge_cooldown -= seconds
                
            if self.himeko_charge >= 3: # worst case: if even possible to be > 3
                for i in team:
                    i.add_energy(self.energy_to_recover) # recovers 10-20 energy for all allies
                # reset cooldowns
                self.energy_cooldown = 30*60
                self.charge_cooldown = 10*60
                self.himeko_charge = 0

        else:
            self.energy_cooldown -= seconds

    def simulate(self, team: list["ABaseGato"], seconds: int = 1):
        # We calculate its energy boost before its actions
        self.energy_buff(seconds, team)

        # Then call the parent simulation (VERY IMPORTANT)
        super().simulate(team, seconds)
