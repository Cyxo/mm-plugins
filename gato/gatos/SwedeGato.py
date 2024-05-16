from ABaseGato import ABaseGato, require_alive

class SwedeGato(ABaseGato):
    """
        > A gato with 500% base efficiency.
    """

    IMAGE = "https://i.ibb.co/mNddLB0/swede-gato.png"
    ANIMATIONS = "swedegato"
    DISPLAY_NAME = "Pistachio Sesame"
    RARITY = 6

    base_efficiency: float = 5.0


    def simulate(self, team: list["ABaseGato"], seconds: int = 1):
        super().simulate(team, seconds)