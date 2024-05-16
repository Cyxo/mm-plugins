import importlib
import os
import sys
DIR = os.path.dirname(__file__)
sys.path.append(DIR)

# Gatos

import ABaseGato
importlib.reload(ABaseGato)

import SwedeGato
import ReiGato
import MapleGato
import MakGato
import ExampleGato, LNYGato
import SeeleGato
import QingqueGato
import HertaGato
import FuxuanGato
import ClaraGato
import BladeGato
import GuinaifenGato
import KafkaGato
import HimekoGato
import ArgentiGato
import DanHengGato
import NormalGato

importlib.reload(SwedeGato)
importlib.reload(ReiGato)
importlib.reload(MapleGato)
importlib.reload(MakGato)
importlib.reload(LNYGato)
importlib.reload(ExampleGato)
importlib.reload(SeeleGato)
importlib.reload(QingqueGato)
importlib.reload(HertaGato)
importlib.reload(FuxuanGato)
importlib.reload(ClaraGato)
importlib.reload(BladeGato)
importlib.reload(GuinaifenGato)
importlib.reload(KafkaGato)
importlib.reload(HimekoGato)
importlib.reload(ArgentiGato)
importlib.reload(DanHengGato)
importlib.reload(NormalGato)

Gato = ABaseGato.ABaseGato
SwedeGato = SwedeGato.SwedeGato
ReiGato = ReiGato.ReiGato
MapleGato = MapleGato.MapleGato
MakGato = MakGato.MakGato
LNYGato = LNYGato.LNYGato
ExampleGato = ExampleGato.ExampleGato
SeeleGato = SeeleGato.SeeleGato
QingqueGato = QingqueGato.QingqueGato
HertaGato = HertaGato.HertaGato
FuxuanGato = FuxuanGato.FuxuanGato
ClaraGato = ClaraGato.ClaraGato
BladeGato = BladeGato.BladeGato
GuinaifenGato = GuinaifenGato.GuinaifenGato
KafkaGato = KafkaGato.KafkaGato
HimekoGato = HimekoGato.HimekoGato
ArgentiGato = ArgentiGato.ArgentiGato
DanHengGato = DanHengGato.DanHengGato
NormalGato = NormalGato.NormalGato

GATOS: list[Gato] = [
    SwedeGato,
    ReiGato,
    MapleGato,
    MakGato,
    LNYGato,
    ExampleGato,
    SeeleGato,
    QingqueGato,
    HertaGato,
    FuxuanGato,
    ClaraGato,
    BladeGato,
    GuinaifenGato,
    KafkaGato,
    HimekoGato,
    ArgentiGato,
    DanHengGato,
    NormalGato
]

## Items

import ABaseItem
importlib.reload(ABaseItem)
Item = ABaseItem.ABaseItem

# Consumables

import AConsumable
importlib.reload(AConsumable)
import ViewGato as ViewGato
importlib.reload(ViewGato)

import RedPacketConsumable, TrashConsumable, MedkitConsumable, \
    AvocadoToastConsumable, CatTreatsConsumable, SwedishFishConsumable, \
    DefibrilatorConsumable, FeatherTeaserConsumable, SalmonConsumable, \
    YaoshiConsumable

importlib.reload(RedPacketConsumable)
importlib.reload(TrashConsumable)
importlib.reload(MedkitConsumable)
importlib.reload(AvocadoToastConsumable)
importlib.reload(CatTreatsConsumable)
importlib.reload(SwedishFishConsumable)
importlib.reload(DefibrilatorConsumable)
importlib.reload(FeatherTeaserConsumable)
importlib.reload(SalmonConsumable)
importlib.reload(YaoshiConsumable)

Consumable = AConsumable.AConsumable
RedPacketConsumable = RedPacketConsumable.RedPacketConsumable
TrashConsumable = TrashConsumable.TrashConsumable
MedkitConsumable = MedkitConsumable.MedkitConsumable
AvocadoToastConsumable = AvocadoToastConsumable.AvocadoToastConsumable
CatTreatsConsumable = CatTreatsConsumable.CatTreatsConsumable
SwedishFishConsumable = SwedishFishConsumable.SwedishFishConsumable
DefibrilatorConsumable = DefibrilatorConsumable.DefibrilatorConsumable
FeatherTeaserConsumable = FeatherTeaserConsumable.FeatherTeaserConsumable
SalmonConsumable = SalmonConsumable.SalmonConsumable
YaoshiConsumable = YaoshiConsumable.YaoshiConsumable

CONSUMABLES: list[AConsumable.AConsumable] = [
    RedPacketConsumable,
    TrashConsumable,
    MedkitConsumable,
    AvocadoToastConsumable,
    CatTreatsConsumable,
    SwedishFishConsumable,
    DefibrilatorConsumable,
    FeatherTeaserConsumable,
    SalmonConsumable
]

# Equipments

import AEquipment
importlib.reload(AEquipment)

import EfficiencyFoodEq, FakeMouseEq

importlib.reload(EfficiencyFoodEq)
importlib.reload(FakeMouseEq)

EfficiencyFoodEq = EfficiencyFoodEq.EfficiencyFoodEq
FakeMouseEq = FakeMouseEq.FakeMouseEq

EQUIPMENTS: list[AEquipment.AEquipment] = [FakeMouseEq]

# Team equipments

import MedicalInsuranceTEq

importlib.reload(MedicalInsuranceTEq)

MedicalInsuranceTEq = MedicalInsuranceTEq.MedicalInsuranceTEq

TEAM_EQUIPMENTS: list[AEquipment.AEquipment] = [MedicalInsuranceTEq]

# All items together

ALL_ITEMS: list[Item] = CONSUMABLES+EQUIPMENTS+TEAM_EQUIPMENTS+GATOS+[EfficiencyFoodEq,YaoshiConsumable]

items_helper = {v.__name__: v for v in ALL_ITEMS}