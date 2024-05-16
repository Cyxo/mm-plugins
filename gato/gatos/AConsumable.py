from abc import abstractmethod

from discord.ext.commands import Context

from ABaseItem import ABaseItem, ItemType


class AConsumable(ABaseItem):
    """**Abstract class** to implement for every consumable."""

    ITEM_TYPE: ItemType = ItemType.CONSUMABLE
    """This is just because AConsumable extends ABaseItem. **DON'T OVERRIDE IT**, it would make no sense..."""


    @abstractmethod
    async def consume(self, ctx: Context, gatogame):
        """**Abstract method** to implement for all consumables.

        :param ctx: Discord context from the ?consume command, used to send back interactions and messages to the user.
        :type ctx: commands.Context
        """
        return True
