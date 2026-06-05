import importlib
import copy
import io
import random
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CODE_DIR = PROJECT_ROOT / "code"
FIXTURE = PROJECT_ROOT / "tests" / "fixtures" / "fplreview_golden.csv"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

fpl_module = importlib.import_module("fpl")
from Algorithm import Algorithm
from Population import Population
from fpl import fpl
from scenario import Scenario


KNOWN_SQUAD_IDS = [
    201,
    202,
    204,
    205,
    206,
    207,
    208,
    211,
    212,
    213,
    214,
    215,
    218,
    219,
    220,
]


class ExistingSquadOptimizerTests(unittest.TestCase):
    def setUp(self):
        self.original_players = fpl_module.players
        self.original_gameweek = fpl_module.gameweek
        self.original_forecastweeks = fpl_module.forecastweeks
        self.random_state = random.getstate()
        fpl_module.gameweek = 3
        fpl_module.forecastweeks = 6
        fpl_module.players = fpl.load_fplreview_players(FIXTURE)
        by_id = {player["id"]: player for player in fpl_module.players}
        self.scenario = Scenario(
            gameweek=3,
            bank=7,
            saved_free_transfers=2,
            current_squad=[by_id[player_id] for player_id in KNOWN_SQUAD_IDS],
            source="test-scenario.json",
        )

    def tearDown(self):
        fpl_module.players = self.original_players
        fpl_module.gameweek = self.original_gameweek
        fpl_module.forecastweeks = self.original_forecastweeks
        random.setstate(self.random_state)

    def test_scenario_population_starts_from_current_squad(self):
        random.seed(7)
        population = Population(4, True, scenario=self.scenario)

        for individual in population.individuals:
            self.assertEqual(
                [player["id"] for player in individual.genes[:15]],
                KNOWN_SQUAD_IDS,
            )
            self.assertEqual(len(individual.genes), len(population.individuals[0].genes))

    def test_scenario_transfer_pattern_can_use_saved_free_transfers_in_first_week(self):
        random.seed(2)
        first_week_counts = {
            Population(1, True, scenario=self.scenario).get_individual(0).genes[-2][0]
            for _ in range(30)
        }

        self.assertTrue(first_week_counts.issubset({0, 1, 2}))
        self.assertGreater(max(first_week_counts), 0)

    def test_scenario_transfer_pattern_caps_saved_free_transfers_at_five(self):
        five_transfer_scenario = Scenario(
            gameweek=3,
            bank=7,
            saved_free_transfers=5,
            current_squad=self.scenario.current_squad,
            source="five-transfer-scenario.json",
        )

        for seed in range(50):
            random.seed(seed)
            pattern = Population(1, True, scenario=five_transfer_scenario).get_individual(0).genes[-2]
            self.assertEqual(len(pattern), fpl_module.transferweeks)
            self.assertLessEqual(max(pattern), 5)

    def test_fresh_team_transfer_pattern_still_skips_first_week(self):
        random.seed(7)
        population = Population(4, True)
        squads = set()

        for individual in population.individuals:
            self.assertEqual(individual.genes[-2][0], 0)
            squads.add(tuple(player["id"] for player in individual.genes[:15]))

        self.assertGreater(len(squads), 1)

    def test_evolved_scenario_population_keeps_context_and_genome_shape(self):
        random.seed(7)
        population = Population(6, True, scenario=self.scenario)

        with redirect_stdout(io.StringIO()):
            evolved = Algorithm.evolve_population(population, 1)

        self.assertIs(evolved.scenario, self.scenario)
        self.assertEqual(evolved.size(), population.size())
        self.assertTrue(all(individual.size() == population.get_individual(0).size() for individual in evolved.individuals))
        self.assertTrue(all(isinstance(individual.genes[-1], list) for individual in evolved.individuals))
        for individual in evolved.individuals:
            self.assertEqual(
                [player["id"] for player in individual.genes[:15]],
                KNOWN_SQUAD_IDS,
            )

    def test_scenario_score_uses_scenario_bank(self):
        team = list(self.scenario.current_squad)
        team.append([0, 0, 0, 0])
        team.append([0, 0, 0, 0])

        score = fpl.scoreteam(team, scenario=self.scenario)

        self.assertGreater(score, 0)
        self.assertEqual(fpl.bank, self.scenario.bank)

    def test_scenario_score_can_apply_first_week_transfers(self):
        original_transfer = fpl.transfer
        calls = []

        def recording_transfer(team, week, playerindex, display, boostweek, tcweek, aooweek, scenario=None):
            calls.append((week, playerindex, scenario))
            return team

        try:
            fpl.transfer = staticmethod(recording_transfer)
            transfer_candidate = [
                player
                for player in fpl_module.players
                if player["id"] not in KNOWN_SQUAD_IDS
            ][0]
            scenario_team = list(self.scenario.current_squad)
            scenario_team.append(transfer_candidate)
            scenario_team.append([1, 0, 0, 0])
            scenario_team.append([0, 0, 0, 0])

            fresh_team = list(self.scenario.current_squad)
            fresh_team.append(transfer_candidate)
            fresh_team.append([1, 0, 0, 0])
            fresh_team.append([0, 0, 0, 0])

            fpl.scoreteam(scenario_team, scenario=self.scenario)
            fpl.scoreteam(fresh_team)
        finally:
            fpl.transfer = original_transfer

        self.assertEqual(calls, [(1, 15, self.scenario)])

    def test_scenario_score_accepts_transfer_and_updates_bank(self):
        players = copy.deepcopy(fpl_module.players)
        by_id = {player["id"]: player for player in players}
        squad = [by_id[player_id] for player_id in KNOWN_SQUAD_IDS]
        transfer_candidate = by_id[222]
        transfer_candidate["now_cost"] = by_id[220]["sellprice"] + self.scenario.bank
        transfer_candidate["1"] = 30.0
        transfer_candidate["2"] = 30.0
        transfer_candidate["3"] = 30.0
        transfer_candidate["4"] = 30.0
        transfer_candidate["5"] = 30.0
        transfer_candidate["6"] = 30.0
        scenario = Scenario(
            gameweek=3,
            bank=self.scenario.bank,
            saved_free_transfers=2,
            current_squad=squad,
            source="accepted-transfer-scenario.json",
        )
        team = list(squad)
        team.append(transfer_candidate)
        team.append([1, 0, 0, 0])
        team.append([0, 0, 0, 0])

        score = fpl.scoreteam(team, scenario=scenario)

        self.assertGreater(score, 0)
        self.assertEqual(fpl.bank, 0)

    def test_scenario_score_allows_owned_squad_above_fresh_budget(self):
        expensive_squad = copy.deepcopy(self.scenario.current_squad)
        for player in expensive_squad:
            player["now_cost"] += 20
        expensive_scenario = Scenario(
            gameweek=3,
            bank=7,
            saved_free_transfers=2,
            current_squad=expensive_squad,
            source="expensive-scenario.json",
        )
        team = list(expensive_squad)
        team.append([0, 0, 0, 0])
        team.append([0, 0, 0, 0])

        self.assertGreater(fpl.teamvalue(team), fpl_module.budget)
        self.assertFalse(fpl.validteam(team))
        self.assertGreater(fpl.scoreteam(team, scenario=expensive_scenario), 0)


if __name__ == "__main__":
    unittest.main()
