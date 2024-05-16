from abc import ABC
from enum import Enum
from random import random

import discord


class ItemType(Enum):
    CONSUMABLE = 1
    EQUIPMENT = 2
    TEAM_EQUIPMENT = 3
    GATO = 4


class ABaseItem(ABC):
    """**Abstract class** to implement for every item (yes, gatos are items).

    Attributes starting with a `_` should not be modified manually.
    Attributes in CAPS are constants."""

    IMAGE: str = "https://i.ibb.co/9n5gT9D/download.png"
    """Sprite of the item. **OVERRIDE IT!**"""

    ANIMATIONS: str = "mooncakegato"
    """A reference to a key in `animations.json`. **OVERRIDE IT!**"""

    DISPLAY_NAME: str = "Base Item"
    """Display name of this item. **OVERRIDE IT!**"""

    RARITY: int = 3
    """Rarity of the item in stars (3-5). **OVERRIDE IT!**"""

    ITEM_TYPE: ItemType = ItemType.CONSUMABLE
    """Type of the item. **OVERRIDE IT!**"""

    VALUES_TO_SAVE = []
    """Attributes that will be saved when exporting the gato to JSON. *Can be completed with custom attributes.*"""

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_json(self):
        """Exports an item to JSON.

        :return: A dict containing the item's class name, and all the values specified in :py:attr:`VALUES_TO_SAVE`.
        :rtype: dict
        """
        return {
            "type": self.__class__.__name__,
            "values": dict((val, getattr(self, val)) for val in self.VALUES_TO_SAVE)
        }

    @classmethod
    def get_embed(cls):
        description = f"# {cls.DISPLAY_NAME}\n"
        description += f"{cls.__doc__}"

        embed = discord.Embed(
            title=cls.DISPLAY_NAME,
            description=description,
            colour=discord.Colour.teal()
        )
        embed.set_image(url=cls.IMAGE)
        return embed

    @classmethod
    def from_json(cls, json: dict):
        """Class method to import an item from JSON.

        :classmethod:
        :param json: A dict exported by :py:meth:`to_json`.
        :type json: dict
        :return: The imported item
        :rtype: :py:class:`ABaseItem`
        """
        return cls(**json["values"])
