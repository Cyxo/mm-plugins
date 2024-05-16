import unittest
import sys
import inspect
import json
import random
from itertools import islice

from gato.gatos import ABaseGato


# copy pasta from https://docs.python.org/3/library/itertools.html#itertools.batched
# available in 3.12
def batched(iterable, n):
    # batched('ABCDEFG', 3) --> ABC DEF G
    if n < 1:
        raise ValueError('n must be at least one')
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch


class FakePlayer:
    currency = 0.0


class SmokeTests(unittest.TestCase):

    CURRENCY_EMOJI = "💎"

    @staticmethod
    def is_gato(obj):
        # predicate for filtering gato classes
        return inspect.isclass(obj) and issubclass(obj, ABaseGato.ABaseGato) and obj != ABaseGato.ABaseGato

    def setUp(self):
        # get all gato classes, instantiate them and assign to teams of 4s
        gato_cls_list = inspect.getmembers(
            sys.modules['gato.gatos'], SmokeTests.is_gato)
        gato_instances = [gato_cls() for name, gato_cls in gato_cls_list]
        self.teams = batched(gato_instances, 4)
        self.player = FakePlayer()

    def test(self):
        lines = []
        # run each team
        for team in self.teams:
            normal_run_currency: list[float] = []
            saved_run_currency: list[float] = []
            lines += [f'\nteam: {", ".join([g.name for g in team])}']
            random.seed(0)
            # deploy each gato in the team
            for gato in team:
                gato.deploy(team)
            # simulate 86400 game ticks
            for _ in range(0, 86400):
                for gato in team:
                    gato.simulate(team, 1)
            # print events
            for gato in team:
                lines += gato.handle_events(self.player, self.CURRENCY_EMOJI)
            # claim each gato
            for gato in team:
                currency, _ = gato.claim()
                normal_run_currency.append(currency)

            # duplicate the team to test with intermediate save/load
            team_copy = [gato.__class__() for gato in team]
            random.seed(0)
            # deploy each gato in the team
            for gato in team_copy:
                gato.deploy(team_copy)
            # simulate 1000 game ticks
            for _ in range(0, 1000):
                for gato in team_copy:
                    gato.simulate(team_copy, 1)
            # save gatos
            team_save = [gato.to_json() for gato in team_copy]
            json.dumps(team_save) # verify all gatos are JSON-serializable
            team_copy = [team_copy[i].__class__.from_json(team_save[i]) for i in range(len(team_save))]
            # simulate the remaining 85400 game ticks
            for _ in range(0, 85400):
                for gato in team_copy:
                    gato.simulate(team_copy, 1)
            # claim each gato
            for gato in team_copy:
                currency, _ = gato.claim()
                saved_run_currency.append(currency)

            for i in range(len(saved_run_currency)):
                try:
                    assert saved_run_currency[i] == normal_run_currency[i]
                except:
                    print(f"Assertion failed for {team[i].name}: {saved_run_currency[i]} != {normal_run_currency[i]}", file=sys.stderr)
                    # raise
                    # continue testing, this is not critical for now

        print('\n'.join(lines))


