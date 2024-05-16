from abc import ABC, abstractmethod
from functools import wraps
from random import random, randint, choice

import discord

from ABaseItem import ABaseItem, ItemType


def require_alive(function):
    """Decorator that only executes a function if the gato has not fainted. **Warning:** Don't add that to functions that shouldn't return `None`."""
    @wraps(function)
    def new_function(gato: "ABaseGato", *args, **kwargs):
        if not gato._fainted:
            return function(gato, *args, **kwargs)

    return new_function

def check_used_equip(function):
    """Decorator that removes used up equipment from the gato."""
    @wraps(function)
    def new_function(gato: "ABaseGato", *args, **kwargs):
        uu = []
        for i, eq in enumerate(gato.equipments):
            if eq.used_up:
                uu.append(i)
        if len(uu) > 0:
            gato.equipments.pop(*uu)
        return function(gato, *args, **kwargs)

    return new_function


class ABaseGato(ABaseItem):
    """**Abstract class** to implement for every gato.

    Attributes starting with a `_` should not be modified manually.
    Attributes in CAPS are constants."""

    IMAGE: str = "https://i.ibb.co/9n5gT9D/download.png"
    """Sprite of the gato. **OVERRIDE IT!**"""

    ANIMATIONS: str = "mooncakegato"
    """A reference to a key in `animations.json`. **OVERRIDE IT!**"""

    DISPLAY_NAME: str = "Base Gato"
    """Display name of this gato class. **OVERRIDE IT!**"""

    RARITY: int = 3
    """Rarity of the gato in stars (3-5). **OVERRIDE IT!**"""

    EVENT_DESCRIPTIONS = {
        "fainted": "fainted.",
        "bitten": "is angry and bites you (x{count}). You lose **{amount}** {currency} in total"
    }
    """Description for the gato's events. *Can be overriden or completed with custom events.*
    For example, `SkellyGato` has a custom event called `"resurrect"` with a custom description."""

    BASE_EARN_RATE: float = 1/16
    """Number of currency per second the gato earns. **DON'T OVERRIDE IT**, rather override :py:attr:`base_efficiency`."""

    BITE_CHANCE: float = 1/100
    """Base chance to get bitten."""

    VALUES_TO_SAVE = [
        "name",
        "mood",
        "health",
        "hunger",
        "energy",
        "health",
        "efficiency_boosts",
        "damage_reductions",
        "hunger_reductions",
        "mood_loss_reductions",
        "energy_loss_reductions",
        "eidolon",
        "friendship",
        "_time_deployed",
        "claimed_today",
        "fetched_currency",
        "fetched_objects"
    ]
    """Attributes that will be saved when exporting the gato to JSON. *Can be overriden or completed with custom attributes.*"""

    ITEM_TYPE = ItemType.GATO
    """This is just because ABaseGato now extends ABaseItem. **DON'T OVERRIDE IT**, it would make no sense..."""

    RANDOM_OBJECT_WEIGHTS = {
        "TrashConsumable": 10,
        "MedkitConsumable": 10,
        "AvocadoToastConsumable": 10,
        "CatTreatsConsumable": 10,
        "SwedishFishConsumable": 10,
        "DefibrilatorConsumable": 10,
        "FeatherTeaserConsumable": 10,
        "SalmonConsumable": 10,
        "FakeMouseEq": 10,
        "MedicalInsuranceTEq": 1
    }
    """Weight of each object when fetching a random object. *Can be overriden or completed with custom objects.*"""


    max_mood: float = 100.0
    """Maximum value for the :py:attr:`mood` stat. *You can override that.*"""

    max_hunger: float = 100.0
    """Maximum value for the :py:attr:`hunger` stat. *You can override that.*"""

    max_energy: float = 100.0
    """Maximum value for the :py:attr:`energy` stat. *You can override that.*"""

    max_health: float = 100.0
    """Maximum value for the :py:attr:`health` stat. *You can override that.*"""


    mood: float
    """Current value for the :py:attr:`mood` stat. Chances to get bitten when :py:attr:`mood` is low. Updated in real time by the :py:meth:`lose_stats_over_time` method when deployed."""

    hunger: float
    """Current value for the :py:attr:`hunger` stat. Loses health when :py:attr:`hunger` is low. Updated in real time by the :py:meth:`lose_stats_over_time` method when deployed."""

    energy: float
    """Current value for the :py:attr:`energy` stat. Reduces efficiency when :py:attr:`energy` is low. Updated in real time by the :py:meth:`lose_stats_over_time` method when deployed."""

    health: float
    """Current value for the :py:attr:`health` stat. Faints when :py:attr:`health` reaches **0**. Updated in real time by the :py:meth:`lose_stats_over_time` method when deployed."""


    efficiency: float
    """Current value for efficiency stat. Updated in real time by the :py:meth:`compute_currency` method when deployed."""

    base_efficiency: float = 1.0
    """Base efficiency stat. *You can override that.*"""

    luck: float = 1.0
    """Multiplier for the chance to find treasures. *You can override that.*"""

    efficiency_boosts: dict[str, float] = {}
    """Boosts of the efficiency stat. The gato or other gatos can add things to it, with a unique key per gato."""

    damage_reductions: dict[str, float] = {}
    """Reduces damage taken. The gato or other gatos can add things to it, with a unique key per gato."""

    hunger_reductions: dict[str, float] = {}
    """Reduces hunger loss. The gato or other gatos can add things to it, with a unique key per gato."""

    mood_loss_reductions: dict[str, float] = {}
    """Reduces mood loss. The gato or other gatos can add things to it, with a unique key per gato."""

    energy_loss_reductions: dict[str, float] = {}
    """Reduces energy loss. The gato or other gatos can add things to it, with a unique key per gato."""

    friendship: float = 1.0
    """Friendship stat, starts at 1, max 10."""

    claimed_today: int = 0
    """Number of times the rewards of this gato have been claimed today."""


    _fainted: bool = False
    """Becomes :token:`True` if the gato's health is 0. Updated by :py:meth:`add_health`"""

    _events: list[dict] = []
    """List of events. Cleared everytime the rewards are claimed. An event is a dict like `{"event_name": "optional value (can be any type)"}`"""

    _time_deployed: int = 0
    """Number of seconds since the gato has been deployed. Updated in real-time by :py:meth:`simulate`"""


    name: str
    """Name of the gato. Choosen by the owner."""

    eidolon: int
    """Eidolon level of the gato. Starts at 0, max 6."""

    equipments: list[ABaseItem]
    """List of equipments on this gato."""

    fetched_currency: float
    """Amount of currency fetched since last claim."""

    fetched_objects: list[str]
    """Objects fetched since last claim."""


    def __init__(self, **kwargs):
        self.mood = self.max_mood
        self.hunger = self.max_hunger
        self.energy = self.max_energy
        self.health = self.max_health
        self.efficiency = self.base_efficiency

        self.name = self.DISPLAY_NAME
        self.eidolon = 0
        self.fetched_currency = 0

        # Initialize objects to new objects (not shared by the class)
        self._events = []
        self.equipments = []
        self.fetched_objects = []
        self.efficiency_boosts = {}
        self.damage_reductions = {}
        self.hunger_reductions = {}
        self.mood_loss_reductions = {}
        self.energy_loss_reductions = {}

        for k, v in kwargs.items():
            setattr(self, k, v)

        if self.health <= 0.0:
            self._fainted = True

    def to_json(self):
        """Exports a gato to JSON.

        :return: A dict containing the gato's class name, and all the values specified in :py:attr:`VALUES_TO_SAVE`.
        :rtype: dict
        """
        dct = super().to_json()
        dct["equipments"] = [eq.to_json() for eq in self.equipments]
        return dct

    @classmethod
    def from_json(cls, json: dict, items_helper = {}):
        """Class method to import a gato from JSON.

        :classmethod:
        :param json: A dict exported by :py:meth:`to_json`.
        :type json: dict
        :return: The imported gato
        :rtype: :py:class:`ABaseGato`
        """
        gato = cls(**json["values"])
        for itm in json["equipments"]:
            eq = items_helper[itm["type"]].from_json(itm)
            gato.equipments.append(eq)
        return gato

    def get_gato_embed(self):
        description = f"# {self.name}\n"
        description += f"## {self.DISPLAY_NAME}\n"
        description += f"{self.__doc__.format(eidolon=self.eidolon)}\n" + \
            f"❤️ {round(self.health)} / {round(self.max_health)} │ " + \
            f"🍗 {round(self.hunger)} / {round(self.max_hunger)} │ " + \
            f"🌞 {round(self.mood)} / {round(self.max_mood)} │ " + \
            f"⚡ {round(self.energy)} / {round(self.max_energy)}\n" + \
            f"**Friendship:** {int(self.friendship)}/10\n" + \
            f"\n✨ **Eidolon {self.eidolon}**\n\nEquipments:\n"

        for eq in self.equipments:
            description += f"- {eq.DISPLAY_NAME}\n"
        if len(self.equipments) == 0:
            description += "*No equipment*"

        embed = discord.Embed(
            title=self.name,
            description=description,
            colour=discord.Colour.teal()
        )
        embed.set_thumbnail(url=self.IMAGE)
        return embed


    @check_used_equip
    def deploy(self, team: list["ABaseGato"]):
        """Called when a gato is deployed."""

        self._time_deployed = 0
        self.efficiency_boosts = {}
        self.damage_reductions = {}
        self.hunger_reductions = {}
        self.mood_loss_reductions = {}
        self.energy_loss_reductions = {}

        if self.health > 0:
            self._fainted = False

        for eq in self.equipments:
                eq.deploy(self)

    @check_used_equip
    def claim(self):
        """Called everytime the owner claims the rewards of this gato."""
        self._events = []

        if self.friendship < 10 and self.claimed_today < 5:
            self.friendship += 0.1

        self.claimed_today += 1

        for eq in self.equipments:
                eq.claim(self)
        
        objects = self.fetched_objects[:]
        currency = self.fetched_currency

        self.fetched_objects.clear()
        self.fetched_currency = 0

        return currency, objects


    def get_args_for_event(self, event_name: str, values: list) -> dict:
        """Called in :py:meth:`handle_events` to get formatting arguments for specific events.
        The `count` of this event and the `currency` emoji are always included.
        **You can override it if needed**, but be sure to call the super-class method and add to its dict.

        :param event_name: The name/id of the event
        :type event_name: str
        :param values: Values that were passed when adding the event, one element for each event occurence
        :type values: list
        :return: Arguments that will be used to format this event's description.
        :rtype: dict
        """
        args = {}
        if event_name == "bitten":
            args["amount"] = 0
            for value in values:
                args["amount"] += value
        return args


    def handle_events(self, player, CURRENCY_EMOJI: str) -> list[str]:
        """Generate a description line for each event type that happened to this gato and return the list.
        **Don't override it**, rather override :py:meth:`get_args_for_event`

        :param player: Owner of the gatos, used to remove 
        :type player: :py:class:`Player`
        :param CURRENCY_EMOJI: The emoji for this plugin's currency
        :type CURRENCY_EMOJI: str
        :return: A list of description lines for each event type
        :rtype: list[str]
        """

        lines = []

        events_by_type = {}
        for event in self._events:
            for et in event.keys():
                if et not in events_by_type:
                    events_by_type[et] = []
                events_by_type[et].append(event[et])

        for et, values in events_by_type.items():
            line = f"- **{self.name}** "

            args = self.get_args_for_event(et, values)
            args["count"] = len(values)
            args["currency"] = CURRENCY_EMOJI

            if et == "bitten":
                player.currency -= args["amount"]

            line += self.EVENT_DESCRIPTIONS[et].format(**args)
            lines.append(line)

        return lines


    def lose_stats_over_time(self, seconds):
        """Computes stat loss over time. Called by :py:meth:`simulate`. *Can be overriden.*"""
        self.add_hunger(-0.01 * seconds)
        self.add_energy(-0.02 * seconds)

        if self._time_deployed >= 30*60:
            self.add_mood(-0.01 * seconds)

        if self.hunger < 10:
            self.add_health(-0.02 * seconds)

        if self.mood < 10:
            if random() < self.BITE_CHANCE / self.friendship:
                self._events.append({"bitten": randint(2, 10)})


    def compute_currency(self, seconds):
        """Computes efficiency and currency gain over time. Called by :py:meth:`simulate`. *Can be overriden.*"""
        self.efficiency = self.base_efficiency + sum(self.efficiency_boosts.values())
        if self.energy < 10:
            self.efficiency -= 0.2
        elif self.energy < 20:
            self.efficiency -= 0.1

        return seconds * self.BASE_EARN_RATE * self.efficiency


    def random_object(self, seconds):
        """Computes random reward findings. Called by :py:meth:`simulate`. *Can be overriden.*"""
        objects = []
        if self._time_deployed % 60 == 0 and self.efficiency >= 1:
            if random() < self.luck / 100:
                cumulative_items = []
                for k, v in self.RANDOM_OBJECT_WEIGHTS.items():
                    cumulative_items += [k]*v
                obj = choice(cumulative_items)
                objects.append(obj)

        return objects


    @abstractmethod
    @check_used_equip
    @require_alive
    def simulate(self, team: list["ABaseGato"], seconds: int = 1):
        """Runs a simulation of the gato.
        **Called pretty much every seconds.**
        Abstract method, **needs to be overriden**. Overriding method should still call superclass method (see :py:class:`ExampleGato`).
        Returns 0-values when gato is fainted.

        :param team: The team the gato is deployed in. Can be used for team-based buffs.
        :type team: list[:py:class:`ABaseGato`]
        :param seconds: Simulation duration in seconds, defaults to 1.
        :type seconds: int, optional
        :return: The amount of currency and the list of objects gathered by the gato.
        :rtype: tuple[float, list[str]]
        """

        self._time_deployed += seconds

        self.lose_stats_over_time(seconds)

        currency = self.compute_currency(seconds)

        objects = self.random_object(seconds)

        for eq in self.equipments:
            eq.simulate(self, seconds)

        self.fetched_currency += currency
        self.fetched_objects += objects


    @require_alive
    def add_health(self, amount: float, allow_overflow: bool = False):
        """Affect a gato's health within its limits.
        Amount can be negative.
        Use this rather than modifying :py:attr:`health` directly.
        Doesn't work when gato is fainted.
        Also sets :py:attr:`_fainted` when :py:attr:`health` is 0.
        *Can be overriden.*

        :param amount: Amount of health to add.
        :type amount: float
        """

        if amount < 0:
            amount = amount * max(0, 1 - sum(self.damage_reductions.values()))

        self.health += amount

        if self.health > self.max_health and not allow_overflow:
            self.health = self.max_health
        elif self.health <= 0.0:
            self.health = 0.0
            self._fainted = True
            self._events.append({"fainted": None})


    @require_alive
    def add_mood(self, amount: float, allow_overflow: bool = False):
        """Affect a gato's mood within its limits.
        Amount can be negative.
        Use this rather than modifying :py:attr:`mood` directly.
        Doesn't work when gato is fainted.
        *Can be overriden.*

        :param amount: Amount of mood to add.
        :type amount: float
        """

        if amount < 0:
            amount = amount * max(0, 1 - sum(self.mood_loss_reductions.values()))

        self.mood += amount

        if self.mood > self.max_mood and not allow_overflow:
            self.mood = self.max_mood
        elif self.mood <= 0.0:
            self.mood = 0.0


    @require_alive
    def add_hunger(self, amount: float, allow_overflow: bool = False):
        """Affect a gato's hunger within its limits.
        Amount can be negative.
        Use this rather than modifying :py:attr:`hunger` directly.
        Doesn't work when gato is fainted.
        *Can be overriden.*

        :param amount: Amount of hunger to add.
        :type amount: float
        """

        if amount < 0:
            amount = amount * max(0, 1 - sum(self.hunger_reductions.values()))

        self.hunger += amount

        if self.hunger > self.max_hunger and not allow_overflow:
            self.hunger = self.max_hunger
        elif self.hunger <= 0.0:
            self.hunger = 0.0


    @require_alive
    def add_energy(self, amount: float, allow_overflow: bool = False):
        """Affect a gato's energy within its limits.
        Amount can be negative.
        Use this rather than modifying :py:attr:`energy` directly.
        Doesn't work when gato is fainted.
        *Can be overriden.*

        :param amount: Amount of energy to add.
        :type amount: float
        """

        if amount < 0:
            amount = amount * max(0, 1 - sum(self.energy_loss_reductions.values()))

        self.energy += amount

        if self.energy > self.max_energy and not allow_overflow:
            self.energy = self.max_energy
        elif self.energy <= 0.0:
            self.energy = 0.0


    def set_eidolon(self, value: int):
        """Setter for a gato's eidolon value.
        Value must be an integer between 0 and 6 (inclusive).
        Use this rather than modifying :py:attr:`eidolon` directly.
        *Can be overriden.* 

        :param amount: New eidolon value to set.
        :type amount: int
        """
        
        # clamp value to [0, 6]
        self.eidolon = max(min(value, 6), 0)
