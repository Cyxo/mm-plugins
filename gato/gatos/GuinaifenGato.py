from datetime import datetime, timezone

from ABaseGato import ABaseGato, require_alive


class GuinaifenGato(ABaseGato):
    """
        > Fav Food: Shumai
        > Upon deployment Increases all allies’ energy and mood by 20 (daily limit of 2). After going under 100, decreases energy/mood consumption by 10%. 
        > Eidolons: e1->e5 (decreases mood/energy consumption by 2%)
        > E6: increases mood/energy gained upon deployment to 25.
    """

    IMAGE: str = "https://i.ibb.co/6sBX02z/guinaifen-gato.png"
    ANIMATIONS: str = "guinaifengato"
    DISPLAY_NAME: str = "Troublemaker"
    RARITY: int = 4
    VALUES_TO_SAVE = ABaseGato.VALUES_TO_SAVE + [
        "recent_stats_buff_ts"
    ]

    GUINAIFEN_STATS_UP_EVENT_TYPE: str = "guinaifen_stats_up"
    GUINAIFEN_STATS_LOSS_DOWN_EVENT_TYPE: str = "guinaifen_stats_loss_down"
    EVENT_DESCRIPTIONS: dict[str, str] = ABaseGato.EVENT_DESCRIPTIONS | {
        GUINAIFEN_STATS_UP_EVENT_TYPE: "increased energy and mood for all allies!",
        GUINAIFEN_STATS_LOSS_DOWN_EVENT_TYPE: "reduced energy and/or mood loss for allies! (x{count})",
    }
    GUINAIFEN_ENERGY_LOSS_REDUCTION_KEY: str = "guinaifen_energy_loss_reduction"
    GUINAIFEN_MOOD_LOSS_REDUCTION_KEY: str = "guinaifen_mood_loss_reduction"

    # Mutable state variables used for this gato
    # Timestamps of recent deploy time buffs
    recent_stats_buff_ts: list[str] = []

    def deploy(self, team: list["ABaseGato"]):
        """Increase mood and energy for the team on deploy"""

        super().deploy(team)

        # Check if we've already buffed allies twice today (utc), skip if so
        now = datetime.now(timezone.utc)
        self.recent_stats_buff_ts = [
            ts for ts in self.recent_stats_buff_ts if datetime.fromisoformat(ts).date() == now.date()]
        if len(self.recent_stats_buff_ts) >= 2:
            return

        # Otherwise, apply buff
        buff_amount = 20 if self.eidolon < 6 else 25
        for g in team:
            # increase energy and mood
            g.add_energy(buff_amount, allow_overflow=True)
            g.add_mood(buff_amount, allow_overflow=True)
        self.recent_stats_buff_ts.append(now.isoformat())

        # event
        self._events.append({self.GUINAIFEN_STATS_UP_EVENT_TYPE: None})

    def simulate(self, team: list["ABaseGato"], seconds: int = 1):
        """Delegates to base method"""

        reduction_amount = 0.1 + (0.02 * min(self.eidolon, 5))
        for g in team:
            if g.energy < 100 and self.GUINAIFEN_ENERGY_LOSS_REDUCTION_KEY not in g.energy_loss_reductions:
                g.energy_loss_reductions[self.GUINAIFEN_ENERGY_LOSS_REDUCTION_KEY] = reduction_amount
                self._events.append(
                    {self.GUINAIFEN_STATS_LOSS_DOWN_EVENT_TYPE: None})
            if g.mood < 100 and self.GUINAIFEN_MOOD_LOSS_REDUCTION_KEY not in g.mood_loss_reductions:
                g.mood_loss_reductions[self.GUINAIFEN_MOOD_LOSS_REDUCTION_KEY] = reduction_amount
                self._events.append(
                    {self.GUINAIFEN_STATS_LOSS_DOWN_EVENT_TYPE: None})
        super().simulate(team, seconds)
