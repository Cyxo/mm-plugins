from abc import abstractmethod

import discord
from discord.ext import commands

from ABaseItem import ABaseItem, ItemType


class AEquipment(ABaseItem):
    """**Abstract class** to implement for every equipment."""

    ITEM_TYPE: ItemType = ItemType.EQUIPMENT
    """This is just because AConsumable extends ABaseItem. **You can override it to `TEAM_EQUIPMENT`**"""

    VALUES_TO_SAVE = [
        "used_up"
    ]
    """Attributes that will be saved when exporting the gato to JSON. *Can be completed with custom attributes.*"""

    used_up: bool = False
    """Setting it to `True` will remove it from the equipped gato's `equipment`"""

    def deploy(self, gato):
        """Called when the equipped gato is deployed."""
        pass

    def claim(self, gato):
        """Called everytime the owner claims the rewards of the equipped gato."""
        pass

    @abstractmethod
    def simulate(self, gato, seconds: int = 1):
        """Called by the equipped gato in its simulate.
        **Called pretty much every seconds.**
        Abstract method, **needs to be overriden**. Overriding method should still call superclass method (see :py:class:`ExampleGato`).
        Here you can manage buff duration and :py:attr:`used_up`.

        :param gato: The equipped gato.
        :type gato: :py:class:`ABaseGato`
        :param seconds: Simulation duration in seconds, defaults to 1.
        :type seconds: int, optional
        :return: The amount of currency and the list of objects gathered by the gato.
        :rtype: tuple[float, list[str]]
        """
        pass
