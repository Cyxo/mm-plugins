import datetime
import importlib

import discord

import team
importlib.reload(team)
import gatos
importlib.reload(gatos)


class PullsStatus:

    pities: dict[str, dict[str, int]]
    fiftyfifties: dict[str, dict[str, bool]]

    def __init__(self, **kwargs) -> None:
        self.pities = {
            "limited": {
                "5": 0,
                "4": 0
            },
            "permanent": {
                "5": 0,
                "4": 0
            }
        }
        self.fiftyfifties = {
            "limited": {
                "5": True,
                "4": True
            }
        }

        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_json(self):
        return {
            "pities": self.pities,
            "fiftyfifties": self.fiftyfifties
        }

    @classmethod
    def from_json(cls, d: dict):
        return cls(**d)


class Player:

    nursery: list[gatos.Gato]
    pulls_status: PullsStatus
    deployed_team: team.Team
    
    command_channel: int
    ping: bool

    currency: float = 0
    currency_boost: float = 0

    inventory: dict[str, int]
    """ Inventory (dict  item_id -> amount) """

    _pull_view: discord.ui.View
    _last_talked: datetime.datetime
    _talked_this_minute: int
    _vc_earn_rate: float
    _time_in_vc: int # in seconds, resets daily
    _last_day_in_vc: datetime.datetime


    def __init__(self, **kwargs) -> None:
        self.nursery = []
        self.pulls_status = PullsStatus()
        self.deployed_team = None
        self.command_channel = None
        self.ping = True

        self._pull_view = None
        self.inventory = {}
        self.currency = 0.0
        self.currency_boost = 0.0

        self._last_talked = datetime.datetime.now()
        self._talked_this_minute = 0
        self._vc_earn_rate = 0
        self._time_in_vc = 3 * 60 * 60
        self._last_day_in_vc = datetime.datetime(2000, 1, 1)

        for k, v in kwargs.items():
            setattr(self, k, v)


    def to_json(self):
        return {
            "nursery": [gato.to_json() for gato in self.nursery],
            "pulls_status": self.pulls_status.to_json(),
            "deployed_team": self.deployed_team.to_json() if self.deployed_team else None,
            "currency": self.currency,
            "inventory": self.inventory,
            "currency_boost": self.currency_boost,
            "command_channel": self.command_channel,
            "ping": self.ping
        }

    @classmethod
    def from_json(cls, plyr: dict):
        plyr["nursery"] = [gatos.items_helper[g["type"]].from_json(g, gatos.items_helper) for g in plyr["nursery"]]
        plyr["pulls_status"] = PullsStatus.from_json(plyr["pulls_status"])
        plyr["deployed_team"] = team.Team.from_json(plyr["deployed_team"], plyr["nursery"]) if plyr["deployed_team"] else None
        return cls(**plyr)
