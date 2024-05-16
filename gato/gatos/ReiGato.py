from ABaseGato import ABaseGato, require_alive


class ReiGato(ABaseGato):
    # Kit parameters
    ALLIES_BUFF_AMOUNT: int = 20
    MINT_GAIN_COOLDOWN_MINS: int = 20
    MINT_BASE_RESTORE_PERCENTAGE: int = 20
    MINT_RESTORE_THRESHOLD: int = 50
    ENCHANCED_MINT_THRESHOLD: int = 50
    ENCHANCED_MINT_COOLDOWN_REDUCTION_MINS: int = 5
    ENCHANCED_MINT_ADDITIONAL_RESTORE_AMOUNT: int = 20
    ADDITIONAL_RESTORE_PERCENTAGE_PER_EIDOLON: int = 4
    E6_ADDITIONAL_ALLIES_BUFF_AMOUNT: int = 30

    # Kit description
    __doc__ = f"""
        > Fav Food: Chocolate
        > When deployed increase all allies energy and mood by {ALLIES_BUFF_AMOUNT}. 
        > Every {MINT_GAIN_COOLDOWN_MINS} minutes Rei gets 1 stack of mint (max stacks 3) which restore any allies mood and energy by {MINT_BASE_RESTORE_PERCENTAGE}% once they’ve lost a total amount of {MINT_RESTORE_THRESHOLD} mood and hunger. 
        > When Rei’s own mood and hunger decreases by a total amount of {ENCHANCED_MINT_THRESHOLD}, the time to gain stacks of mint is decreased by {ENCHANCED_MINT_COOLDOWN_REDUCTION_MINS} minutes and restores {ENCHANCED_MINT_ADDITIONAL_RESTORE_AMOUNT} more energy/mood back to allies.
        > Eidolons: e1 -> e5: Mood and energy recovery percentage is increased by an additional {ADDITIONAL_RESTORE_PERCENTAGE_PER_EIDOLON}% per eidolon.
        > E6: Gain additional {E6_ADDITIONAL_ALLIES_BUFF_AMOUNT} energy and mood upon deployment.
    """

    # TODO: name & animation
    IMAGE = "https://cdn.discordapp.com/attachments/1198010808672723075/1203291115005153330/reigato.png"
    ANIMATIONS = "reigato"
    DISPLAY_NAME = "Mint Chocolate Parfait"
    RARITY = 5
    VALUES_TO_SAVE = ABaseGato.VALUES_TO_SAVE + [
        "mint_gain_cooldown",
    ]

    REI_STATS_UP_EVENT_TYPE = "rei_stats_up"
    REI_MINT_GAIN_EVENT_TYPE = "rei_mint_gain"
    REI_MINT_RESTORE_EVENT_TYPE = "rei_mint_restore"
    EVENT_DESCRIPTIONS = ABaseGato.EVENT_DESCRIPTIONS | {
        REI_STATS_UP_EVENT_TYPE: "increased all allies' energy and mood! x{count}",
        REI_MINT_GAIN_EVENT_TYPE: "gained a stack of mint! x{count}",
        REI_MINT_RESTORE_EVENT_TYPE: "consumed a stack of mint and restored mood and hunger of an ally! x{count}",
    }

    # Mutable state variables used for this gato
    # Cooldown till a mint stack can be gained again
    mint_gain_cooldown: int = 0
    # Current number of mint stacks
    mint_stacks: int = 0

    def mint(self, team, seconds):
        # Tick down mint gain cd if needed
        if self.mint_gain_cooldown > 0:
            self.mint_gain_cooldown = max(self.mint_gain_cooldown - seconds, 0)

        # Add a stack if not in cooldown or at max
        if self.mint_gain_cooldown <= 0 and self.mint_stacks < 3:
            self.mint_stacks += 1
            self.set_mint_gain_cooldown()
            # Send event
            self._events.append({self.REI_MINT_GAIN_EVENT_TYPE: None})

        # Check ally mood and hunger level and recover mood and energy as necessary if mint stacks available
        gatos = iter(team)
        while self.mint_stacks > 0 and (g := next(gatos, None)) is not None:
            mood_lost = g.max_mood - g.mood
            hunger_lost = g.max_hunger - g.hunger
            if mood_lost + hunger_lost >= self.MINT_RESTORE_THRESHOLD:
                # Calculate percentage increase
                restore_percentage = self.MINT_BASE_RESTORE_PERCENTAGE + \
                    min(5, self.eidolon) * \
                    self.ADDITIONAL_RESTORE_PERCENTAGE_PER_EIDOLON
                mood_restore_amount = g.max_mood * restore_percentage / 100
                energy_restore_amount = g.max_energy * restore_percentage / 100
                # Calculate additional flat increase if enhanced mint
                if self.is_enhanced_mint():
                    mood_restore_amount += self.ENCHANCED_MINT_ADDITIONAL_RESTORE_AMOUNT
                    energy_restore_amount += self.ENCHANCED_MINT_ADDITIONAL_RESTORE_AMOUNT
                # Apply restore
                g.add_mood(mood_restore_amount)
                g.add_energy(energy_restore_amount)
                self.mint_stacks -= 1
                self._events.append({self.REI_MINT_RESTORE_EVENT_TYPE: None})

    def deploy(self, team: list["ABaseGato"]):
        """Increase mood and energy for the team on deploy"""

        # Run base class deploy
        super().deploy(team)

        # Reset mutable states
        self.set_mint_gain_cooldown()
        self.mint_stacks = 0

        # Apply team wide mood and energy buff
        buff_amount = self.ALLIES_BUFF_AMOUNT + \
            (0 if self.eidolon < 6 else self.E6_ADDITIONAL_ALLIES_BUFF_AMOUNT)
        for g in team:
            # increase energy and mood
            g.add_energy(buff_amount, allow_overflow=True)
            g.add_mood(buff_amount, allow_overflow=True)

        # Send event
        self._events.append({self.REI_STATS_UP_EVENT_TYPE: None})

    def simulate(self, team: list["ABaseGato"], seconds: int = 1):
        # Apply self kit effects
        self.mint(team, seconds)

        # Run base class game tick
        return super().simulate(team, seconds)

    def set_mint_gain_cooldown(self):
        cd_mins = self.MINT_GAIN_COOLDOWN_MINS
        if self.is_enhanced_mint():
            cd_mins -= self.ENCHANCED_MINT_COOLDOWN_REDUCTION_MINS
        self.mint_gain_cooldown = cd_mins * 60

    def is_enhanced_mint(self) -> bool:
        mood_lost = self.max_mood - self.mood
        hunger_lost = self.max_hunger - self.hunger
        return mood_lost + hunger_lost >= self.ENCHANCED_MINT_THRESHOLD
