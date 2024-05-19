from ABaseGato import ABaseGato, require_alive


class KafkaGato(ABaseGato):
    """
        > Fav Food: Red Bull
        > Increases all allies’ efficiency by 10% for 20 minutes after every hour.
        > Eidolons: e1->e5 (increases efficiency boost by 1%)
        > E6: (increases time to 22 minutes).
    """

    IMAGE = "https://i.ibb.co/X2vJgrF/kafka-gato.png"
    ANIMATIONS = "kafkagato"
    DISPLAY_NAME = "Shader Cat"
    RARITY = 4
    VALUES_TO_SAVE: list[str] = ABaseGato.VALUES_TO_SAVE + [
        'eff_boost_duration',
        'eff_boost_cooldown',
    ]

    KAFKA_EFF_BOOST_EVENT_TYPE: str = "kafka_eff_boost"
    EVENT_DESCRIPTIONS: dict[str, str] = ABaseGato.EVENT_DESCRIPTIONS | {
        KAFKA_EFF_BOOST_EVENT_TYPE: "boosted efficiency of all allies!  (x{count})",
    }
    KAFKA_EFF_BOOST_KEY: str = "kafka_eff_boost"

    eff_boost_duration: int = 0
    eff_boost_cooldown: int = 0

    @require_alive
    def maybe_apply_eff_boost(self, team, seconds):
        # Update boost duration and cooldown
        if self.eff_boost_duration > 0:
            self.eff_boost_duration = max(self.eff_boost_duration - seconds, 0)
        if self.eff_boost_cooldown > 0:
            self.eff_boost_cooldown = max(self.eff_boost_cooldown - seconds, 0)

        # Remove boost and return if duration ran out and still in cooldown
        if self.eff_boost_duration <= 0 and self.eff_boost_cooldown > 0:
            for g in team:
                g.efficiency_boosts.pop(self.KAFKA_EFF_BOOST_KEY, None)
            return

        # Activate the boost if cd is clear
        if self.eff_boost_cooldown <= 0:
            # Refresh full boost duration and cooldown
            self.eff_boost_duration = 1200 if self.eidolon < 6 else 1320
            self.eff_boost_cooldown = 3600
            # Fire event
            self._events.append({self.KAFKA_EFF_BOOST_EVENT_TYPE: None})

        # Apply efficiency boost
        boost_amount = 0.1 + 0.01 * min(self.eidolon, 5)
        for g in team:
            g.efficiency_boosts[self.KAFKA_EFF_BOOST_KEY] = boost_amount

    def simulate(self, team: list["ABaseGato"], seconds: int = 1):
        # Check and apply efficiency boost if applicable
        self.maybe_apply_eff_boost(team, seconds)

        super().simulate(team, seconds)
