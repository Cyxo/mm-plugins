from collections import Counter
from enum import Enum
import random

from ABaseGato import ABaseGato, require_alive


class RecoverableStat(Enum):
    MOOD = 1
    HUNGER = 2
    ENERGY = 3
    HEALTH = 4
    EFFICIENCY = 5

    def __str__(self):
        return self.name.lower()


class EfficiencyBoost:
    def __init__(self, duration_s, amount):
        self.duration_s = duration_s
        self.amount = amount


class QingqueGato(ABaseGato):
    """
        > Fav Food: Immortal’s Delight
        > Every time a stat bar level decreases, there is a 10% chance 
        > for 2 other stat bars to increase by the decreased amount. 
        > Eidolons: e1->e5 (increases base chance by 2%)
        > e6: increases base chance by 2%, allows efficiency to be increased 
        > at a lowered amount (25% of the stat decreased amount) for the next 
        > 1 minute by the skill and enables jade mechanic. 
        > Jade mechanic: when stat bars are recovered by skill, obtains 
        > a tile matching recovered stats (5 suits in total), and can hold
        > up to 4 tiles at one time. If she has 4 tiles of the same suit, 
        > the next time stats are recovered, the recovered amount is doubled 
        > and her hand is cleared. This double recovery does not generate tiles.
    """

    IMAGE = "https://i.ibb.co/zHR9K98/qingque-gato.png"
    ANIMATIONS = "qingquegato"
    DISPLAY_NAME = "Lucky Snack"
    RARITY = 4
    VALUES_TO_SAVE = ABaseGato.VALUES_TO_SAVE + [
        "e6_tiles",
        "e6_hidden_hand",
        "e6_efficiency_buffs",
    ]

    QQ_EVENT_TYPE_FLOWER_PICK = "qq_flower_pick"
    QQ_EVENT_TYPE_CHERRY_ON_TOP = "qq_cherry_on_top"
    EVENT_DESCRIPTIONS = ABaseGato.EVENT_DESCRIPTIONS | {
        QQ_EVENT_TYPE_FLOWER_PICK: "was lucky and recovered some stats! x{count}",
        QQ_EVENT_TYPE_CHERRY_ON_TOP: "was blessed and recovered double stats! x{count}"
    }
    BUFF_KEY: str = "QQ_eff_buff"

    e6_tiles = []
    e6_hidden_hand = False
    # list of buff entries since QQ will have a stack of many tiny efficiency buffs
    e6_efficiency_buffs = []

    def skill(self, amount: float, exclude: RecoverableStat):
        # Choose 2 other stat to recover
        excluded_stats = {exclude}
        if self.eidolon < 6:
            excluded_stats.add(RecoverableStat.EFFICIENCY)
        target_stats = random.choices(
            [stat for stat in RecoverableStat if stat not in excluded_stats], k=2)

        # Handle jade mechanic
        event_type = self.QQ_EVENT_TYPE_FLOWER_PICK
        if self.eidolon == 6:
            if self.e6_hidden_hand:
                # Apply hidden hand effect if needed
                amount *= 2
                event_type = self.QQ_EVENT_TYPE_CHERRY_ON_TOP
                # Reset hidden hand
                self.e6_tiles = []
                self.e6_hidden_hand = False
            else:
                # Draw tiles and update hand otherwise
                counter = Counter(self.e6_tiles) + Counter(target_stats)
                self.e6_tiles = []
                for stat, count in counter.most_common():
                    self.e6_tiles.extend([stat] * count)
                    if count >= 4:
                        self.e6_hidden_hand = True
                    if len(self.e6_tiles) >= 4:
                        break
                self.e6_tiles = self.e6_tiles[:4]

        # Recover stats
        for stat in target_stats:
            if str(stat) == str(RecoverableStat.MOOD):
                self.add_mood(-amount)
            elif str(stat) == str(RecoverableStat.HUNGER):
                self.add_hunger(-amount)
            elif str(stat) == str(RecoverableStat.ENERGY):
                self.add_energy(-amount)
            elif str(stat) == str(RecoverableStat.HEALTH):
                self.add_health(-amount)
            elif str(stat) == str(RecoverableStat.EFFICIENCY):
                self.add_efficiency_buff(-amount * 0.25)

        # Send event
        self._events.append({event_type: None})

    def add_efficiency_buff(self, amount):
        self.e6_efficiency_buffs.append(EfficiencyBoost(60, amount))

    def update_efficiency_buffs(self, seconds):
        # Sum all active eff buff stacks and apply boost
        self.efficiency_boosts[self.BUFF_KEY] = sum(
            [buff.amount for buff in self.e6_efficiency_buffs])

        # Tick down duration
        for buff in self.e6_efficiency_buffs:
            buff.duration_s -= seconds

        # Kill expired buffs
        self.e6_efficiency_buffs = [
            buff for buff in self.e6_efficiency_buffs if buff.duration_s > 0]

    def skill_threshold(self):
        return 0.1 + 0.02 * self.eidolon

    @require_alive
    def add_health(self, amount: float, allow_overflow: bool = False):
        super().add_health(amount, allow_overflow)
        if amount < 0 and random.random() < self.skill_threshold():
            self.skill(amount, RecoverableStat.HEALTH)

    @require_alive
    def add_mood(self, amount: float, allow_overflow: bool = False):
        super().add_mood(amount, allow_overflow)
        if amount < 0 and random.random() < self.skill_threshold():
            self.skill(amount, RecoverableStat.MOOD)

    @require_alive
    def add_hunger(self, amount: float, allow_overflow: bool = False):
        super().add_hunger(amount, allow_overflow)
        if amount < 0 and random.random() < self.skill_threshold():
            self.skill(amount, RecoverableStat.HUNGER)

    @require_alive
    def add_energy(self, amount: float, allow_overflow: bool = False):
        super().add_energy(amount, allow_overflow)
        if amount < 0 and random.random() < self.skill_threshold():
            self.skill(amount, RecoverableStat.ENERGY)

    def simulate(self, team: list["ABaseGato"], seconds: int = 1):
        # apply efficiency boosts from active buff stacks
        # new stacks generated by losing and recovery stats in this game tick
        # will kick in on the next game tick
        self.update_efficiency_buffs(seconds)
        super().simulate(team, seconds)
