from ABaseGato import ABaseGato, require_alive


class MapleGato(ABaseGato):
    SELF_BUFF_CURRENCY_GAIN_REQUIRED: int = 10
    SELF_ENERGY_LOSS_REDUCTION_PERCENTAGE_PER_STACK: int = 10
    SELF_BUFF_MAX_STACKS: int = 4
    SELF_ADDITIONAL_ENERGY_LOSS_REDUCTION_PERCENTAGE_PER_STACK_PER_EIDOLON: int = 2

    TEAM_BUFF_CURRENCY_GAIN_REQUIRED: int = 40
    TEAM_BUFF_MOOD_BOOST_PERCENTAGE: int = 10
    TEAM_BUFF_MOOD_BOOST_CAP: int = 100
    TEAM_BUFF_EFFICIENCY_BOOST_PERCENTAGE: int = 10
    TEAM_BUFF_EFFICIENCY_BOOST_DURATION_MINS: int = 10
    TEAM_BUFF_ADDITIONAL_EFFICIENCY_BOOST_DURATION_E6: int = 5

    __doc__ = f"""
        > Fav Food:
        > Own energy consumption is decreased by {SELF_ENERGY_LOSS_REDUCTION_PERCENTAGE_PER_STACK}% everytime they gain {SELF_BUFF_CURRENCY_GAIN_REQUIRED} amount of plum blossoms (currency) (can stack up to {SELF_BUFF_MAX_STACKS} times). 
        > Everytime {TEAM_BUFF_CURRENCY_GAIN_REQUIRED} amount of plum blossoms (currency) is gained, restore all allies mood by {TEAM_BUFF_MOOD_BOOST_PERCENTAGE}% and boost efficiency by {TEAM_BUFF_EFFICIENCY_BOOST_PERCENTAGE}% for {TEAM_BUFF_EFFICIENCY_BOOST_DURATION_MINS} minutes (a total amount of {TEAM_BUFF_MOOD_BOOST_CAP} mood can be restored).
        > Eidolons: e1 -> e5: Own energy consumption decrease effect is enhanced by {SELF_ADDITIONAL_ENERGY_LOSS_REDUCTION_PERCENTAGE_PER_STACK_PER_EIDOLON}% per eidolon.
        > e6: Efficiency boost lasts for an additional {TEAM_BUFF_ADDITIONAL_EFFICIENCY_BOOST_DURATION_E6} minutes.
    """

    IMAGE = "https://cdn.discordapp.com/attachments/1198010808672723075/1208681228492865629/maplegato.png"
    ANIMATIONS = "maplegato"
    DISPLAY_NAME = "Midnight Berry"
    RARITY = 5
    VALUES_TO_SAVE = ABaseGato.VALUES_TO_SAVE + [
        "team_buff_applied_count",
        "team_buff_duration",
        "team_buff_mood_quota"
    ]

    MAPLE_EVENT_TYPE_SELF_BUFF = "maple_self_buff"
    MAPLE_EVENT_TYPE_TEAM_BUFF_MOOD = "maple_team_buff_mood"
    MAPLE_EVENT_TYPE_TEAM_BUFF_EFF = "maple_team_buff_eff"
    EVENT_DESCRIPTIONS = ABaseGato.EVENT_DESCRIPTIONS | {
        MAPLE_EVENT_TYPE_SELF_BUFF: "reduced own energy loss!",
        MAPLE_EVENT_TYPE_TEAM_BUFF_MOOD: "boosted an ally's mood! (x{count})",
        MAPLE_EVENT_TYPE_TEAM_BUFF_EFF: "boosted allies' efficiency! (x{count})",
    }
    # dict key to keep track of this gato's buffs
    BUFF_KEY: str = "maple_buff"

    # Mutable state variables used for this gato
    # Number of times team buff has been applied
    team_buff_applied_count: int = 0
    # Remaining duration in seconds for team buff
    team_buff_duration: int = 0
    # Amount of mood buff amount remaining
    team_buff_mood_quota: int = 0
    # Self buff flag for event optimisation (avoids 10k+ events)
    self_buff_event_sent: bool = False

    @require_alive
    def self_buff(self):
        self_buff_stacks = min(self.SELF_BUFF_MAX_STACKS, int(
            self.fetched_currency / self.SELF_BUFF_CURRENCY_GAIN_REQUIRED))
        per_stack_energy_loss_reduction = (self.SELF_ENERGY_LOSS_REDUCTION_PERCENTAGE_PER_STACK +
                                           self.SELF_ADDITIONAL_ENERGY_LOSS_REDUCTION_PERCENTAGE_PER_STACK_PER_EIDOLON * min(5, self.eidolon)) / 100
        self.energy_loss_reductions[self.BUFF_KEY] = self_buff_stacks * \
            per_stack_energy_loss_reduction
        if not self.self_buff_event_sent and self_buff_stacks > 0:
            self._events.append({self.MAPLE_EVENT_TYPE_SELF_BUFF: None})
            self.self_buff_event_sent = True

    @require_alive
    def team_buff(self, team, seconds):
        # Tick down team wide efficency boost duration
        if self.team_buff_duration > 0:
            self.team_buff_duration = max(self.team_buff_duration - seconds, 0)

        # Check currency accumlated since last team buff
        currency_gain_since_last_team_buff = self.fetched_currency - \
            self.team_buff_applied_count * self.TEAM_BUFF_CURRENCY_GAIN_REQUIRED
        if currency_gain_since_last_team_buff >= self.TEAM_BUFF_CURRENCY_GAIN_REQUIRED:
            # Applying team buff
            self.team_buff_applied_count += 1
            # Inc efficiency boost duration
            eff_boost_duration_mins = self.TEAM_BUFF_EFFICIENCY_BOOST_DURATION_MINS + \
                (self.TEAM_BUFF_ADDITIONAL_EFFICIENCY_BOOST_DURATION_E6 if self.eidolon >= 6 else 0)
            self.team_buff_duration += eff_boost_duration_mins * 60
            self._events.append({self.MAPLE_EVENT_TYPE_TEAM_BUFF_EFF: None})
            # Restore mood team wide
            for g in team:
                if self.team_buff_mood_quota > 0:
                    mood_increase = min(
                        self.team_buff_mood_quota, g.max_mood * self.TEAM_BUFF_MOOD_BOOST_PERCENTAGE / 100)
                    g.add_mood(mood_increase)
                    self.team_buff_mood_quota -= mood_increase
                    self._events.append(
                        {self.MAPLE_EVENT_TYPE_TEAM_BUFF_MOOD: None})

        # Apply efficiency boost if duration remaining
        if self.team_buff_duration > 0:
            for g in team:
                g.efficiency_boosts[self.BUFF_KEY] = self.TEAM_BUFF_EFFICIENCY_BOOST_PERCENTAGE / 100
        else:
            for g in team:
                g.efficiency_boosts.pop(self.BUFF_KEY, None)

    def deploy(self, team: list["ABaseGato"]):
        # Reset mood increase quota
        self.team_buff_mood_quota = self.TEAM_BUFF_MOOD_BOOST_CAP

        # Run parent deploy
        super().deploy(team)

    def simulate(self, team: list["ABaseGato"], seconds: int = 1):
        # Run self energy loss reduction buff
        self.self_buff()

        # Run team wide mood restore and efficiency buff
        self.team_buff(team, seconds)

        # Run parent game tick
        super().simulate(team, seconds)
