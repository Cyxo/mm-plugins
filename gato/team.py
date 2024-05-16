from datetime import datetime
from typing import Optional

class Team:

    gatos: list

    deployed_at: Optional[datetime] = None
    pinged_already: bool = False

    def __init__(self, gatos: list, deployed_at = None, pinged_already = False):
        self.deployed_at = deployed_at
        self.gatos = gatos
        self.pinged_already = pinged_already

    def to_json(self):
        return {
            "gatos": [gato.DISPLAY_NAME for gato in self.gatos],
            "deployed_at": None if self.deployed_at is None else self.deployed_at.timestamp(),
            "pinged_already": self.pinged_already
        }

    @classmethod
    def from_json(cls, d: dict, nursery: list):
        gatos = [[gato for gato in nursery if gato.DISPLAY_NAME == DISPLAY_NAME][0] for DISPLAY_NAME in d["gatos"]]
        deployed_at = datetime.fromtimestamp(d["deployed_at"]) if d["deployed_at"] is not None else None
        pinged_already = d["pinged_already"]
        return cls(gatos, deployed_at, pinged_already)
