from datetime import datetime, timezone

from ABaseGato import ABaseGato, require_alive


class FuxuanGato(ABaseGato):
    """
        > Fav Food: Startaro Boba
        > Reduces health decrease of all allies by 20%. 
        > Once HP falls below 50%, restores own HP by 30% 
        > (up to 80% total HP can be recovered, cooldown of 2 hours, daily limit of 2).
        > Eidolons: e1->e5 (reduces health decrease to 30%, 2% per eidolon)
        > E6: (health restored increases to 85% and cooldown decreases by 30 minutes)
    """

    # TODO: name & animation
    IMAGE = "https://i.ibb.co/8bThsz0/fuxuangato.png"
    # ANIMATIONS = "fuxuangato"
    DISPLAY_NAME = "Fuxuan Gato"
    RARITY = 4
    VALUES_TO_SAVE = ABaseGato.VALUES_TO_SAVE + [
        "recent_heal_ts",
        "heal_cooldown"
    ]

    FX_MATRIX_EVENT_TYPE = "fx_matrix_of_prescience"
    FX_HEAL_EVENT_TYPE = "fx_self_heal"
    EVENT_DESCRIPTIONS = ABaseGato.EVENT_DESCRIPTIONS | {
        FX_MATRIX_EVENT_TYPE: "activated matrix of prescience!",
        FX_HEAL_EVENT_TYPE: "flipped and recovered some hp! (x{count})",
    }
    FX_DMG_REDUCTION_KEY: str = "FX_dmg_reduction"

    recent_heal_ts: list[str] = []
    heal_cooldown: int = 0

    def maybe_apply_heal(self, seconds):
        # Tick down heal cd if needed
        if self.heal_cooldown > 0:
            self.heal_cooldown = max(self.heal_cooldown - seconds, 0)

        # Check if we are still within cooldown since last heal, skip if so
        if self.heal_cooldown > 0:
            return

        # Check if we are at or above 50% hp, skip if so
        if self.health >= self.max_health * 0.5:
            return

        # Check if we've already healed twice today (utc), skip if so
        now = datetime.now(timezone.utc)
        self.recent_heal_ts = [
            ts for ts in self.recent_heal_ts if datetime.fromisoformat(ts).date() == now.date()]
        if len(self.recent_heal_ts) >= 2:
            return

        # Now we can heal
        heal_amount = self.max_health * 0.3 if self.eidolon < 6 else self.max_health * 0.35
        self.add_health(heal_amount)
        self.recent_heal_ts.append(now.isoformat())
        self.heal_cooldown = 7200 if self.eidolon < 6 else 5400
        self._events.append({self.FX_HEAL_EVENT_TYPE: None})

    def simulate(self, team: list["ABaseGato"], seconds: int = 1):
        # Run base class game tick to apply stats loss first
        super().simulate(team, seconds)

        # Apply damage reduction to the team if we haven't
        dmg_reduction_amount = 0.2 + 0.02 * min(self.eidolon, 5)
        for gato in team:
            if self.FX_DMG_REDUCTION_KEY not in gato.damage_reductions:
                gato.damage_reductions[self.FX_DMG_REDUCTION_KEY] = dmg_reduction_amount
                self._events.append({self.FX_MATRIX_EVENT_TYPE: None})

        # Apply self heal if applicable
        self.maybe_apply_heal(seconds)
