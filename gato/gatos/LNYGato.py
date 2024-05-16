from random import random

from ABaseGato import ABaseGato, require_alive

class LNYGato(ABaseGato):
    """
        > Finds a Red Packet every hour. Red Packets will give 1000 🌸 in total randomly dispatched accross 10 people who claim it.
    """

    # Override constants
    IMAGE = "https://i.ibb.co/nmrMHWZ/IMG-2328.png"
    ANIMATIONS = "lnygato"
    DISPLAY_NAME = "Lucky Tangerine"
    RARITY = 5
    VALUES_TO_SAVE = ABaseGato.VALUES_TO_SAVE + [
        "find_object_cooldown"
    ]

    # Custom variables used for this gato
    find_object_cooldown: int = 0       # Remaining cooldown until it can find a red packet again


    def random_object(self, seconds):
        # Call superclass method to find base objects
        objects = super().random_object(seconds)

        # Update object finding cooldown
        self.find_object_cooldown -= seconds

        # If the cooldown is over, try to find an object
        if self.find_object_cooldown <= 0:
            # Set base cooldown
            self.find_object_cooldown = 3600

            # Find a Red Packet
            objects.append("RedPacketConsumable")

        # Return found objects
        return objects


    def simulate(self, team: list["ABaseGato"], seconds: int = 1):
        # Then call the parent simulation (VERY IMPORTANT)
        super().simulate(team, seconds)
