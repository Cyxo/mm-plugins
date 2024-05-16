from ABaseGato import ABaseGato, require_alive


class HertaGato(ABaseGato):
    """
        > Fav Food: Ice Cream
        > Increases efficiency by 20% for 20 minutes after every hour.
        > Eidolons: e1->e5 (increases efficiency boost by 2%)
        > E6: (increases time to 30 minutes)
    """

    IMAGE = "https://i.ibb.co/MGcLYqv/herta-gato.png"
    ANIMATIONS = "hertagato"
    DISPLAY_NAME = "Wisteria Cake"
    RARITY = 4
    VALUES_TO_SAVE = ABaseGato.VALUES_TO_SAVE + [
        "buff_duration",
        "buff_cooldown",
    ]

    HERTA_EVENT_TYPE_KURU_KURU = "herta_kuru_kuru"
    EVENT_DESCRIPTIONS = ABaseGato.EVENT_DESCRIPTIONS | {
        HERTA_EVENT_TYPE_KURU_KURU: "kuru kuru! x{count}"
    }

    # Custom variables used for this gato
    buff_duration: int = 0              # Remaining duration for its buff
    buff_cooldown: int = 0              # Remaining cooldown for its buff
    BUFF_KEY: str = "Herta_eff_buff"    # dict key to keep track of this gato's buffs

    @require_alive
    def efficiency_buff(self, seconds):
        # Update buff duration and cooldown
        if self.buff_duration > 0:
            self.buff_duration = max(self.buff_duration - seconds, 0)
        if self.buff_cooldown > 0:
            self.buff_cooldown = max(self.buff_cooldown - seconds, 0)

        # Remove boost and return if duration ran out and still in cooldown
        if self.buff_duration <= 0 and self.buff_cooldown > 0:
            self.efficiency_boosts.pop(self.BUFF_KEY, None)
            return

        # Activate the buff if cd is clear
        if self.buff_cooldown <= 0:
            # Set base cooldown and duration
            self.buff_duration = 1200 if self.eidolon < 6 else 1800
            self.buff_cooldown = 3600

            # Fire event
            self._events.append({self.HERTA_EVENT_TYPE_KURU_KURU: None})

        # Apply efficiency boost
        eidolon_buff_increase = 0.02 * min(self.eidolon, 5)
        self.efficiency_boosts[self.BUFF_KEY] = 0.2 + eidolon_buff_increase

    def simulate(self, team: list["ABaseGato"], seconds: int = 1):
        # We calculate its efficiency boost before its actions
        self.efficiency_buff(seconds)

        # Then call the parent simulation
        super().simulate(team, seconds)
