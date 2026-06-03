import importlib
import io
import random
import sys
import unittest
from collections import Counter
from contextlib import redirect_stdout
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CODE_DIR = PROJECT_ROOT / "code"
FIXTURE = PROJECT_ROOT / "tests" / "fixtures" / "fplreview_golden.csv"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

fpl_module = importlib.import_module("fpl")
from fpl import fpl
from Population import Population
from Algorithm import Algorithm


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


def players_by_id(players):
    return {player["id"]: player for player in players}


def known_squad(players):
    by_id = players_by_id(players)
    team = [by_id[player_id] for player_id in KNOWN_SQUAD_IDS]
    team.append([0, 0, 0, 0])
    team.append([0, 0, 0, 0])
    return team


class FplReviewGoldenFixtureTests(unittest.TestCase):
    def tearDown(self):
        fpl_module.players = []
        fpl_module.fixtures = []

    def test_golden_fixture_imports_balanced_player_pool(self):
        players = fpl.load_fplreview_players(FIXTURE)

        self.assertGreater(len(players), 15)
        counts = Counter(player["element_type"] for player in players)
        self.assertGreaterEqual(counts[1], 2)
        self.assertGreaterEqual(counts[2], 5)
        self.assertGreaterEqual(counts[3], 5)
        self.assertGreaterEqual(counts[4], 3)
        self.assertTrue(all(player["status"] == "a" for player in players))

        bench_midfielder = players_by_id(players)[216]
        self.assertLess(bench_midfielder["lookaheadpoints"], 7.0)
        self.assertEqual(bench_midfielder["status"], "a")

    def test_known_squad_from_golden_fixture_is_valid_and_scores(self):
        players = fpl.load_fplreview_players(FIXTURE)
        team = known_squad(players)

        self.assertEqual(len(team[:15]), 15)
        self.assertEqual(Counter(player["element_type"] for player in team[:15]), {1: 2, 2: 5, 3: 5, 4: 3})
        self.assertLessEqual(fpl.teamvalue(team), fpl_module.budget)
        self.assertTrue(fpl.validteam(team))
        self.assertAlmostEqual(fpl.scoreteam(team), 423.6)

    def test_tiny_seeded_ga_smoke_runs_against_golden_fixture(self):
        fpl_module.players = fpl.load_fplreview_players(FIXTURE)
        random_state = random.getstate()
        try:
            random.seed(7)

            population = Population(6, True)
            initial_fittest_score = population.fitness_of_the_fittest()

            self.assertGreater(initial_fittest_score, 0)

            random.seed(7)
            with redirect_stdout(io.StringIO()):
                evolved = Algorithm.evolve_population(population, 1)
            evolved_fittest = evolved.get_fittest()
            evolved_fittest_score = evolved.get_fitness(evolved_fittest)
            non_elite_individuals = evolved.individuals[1:]
            scoreable_non_elite_individuals = [
                individual
                for individual in non_elite_individuals
                if fpl.validteam(individual.genes[:15]) and fpl.scoreteam(individual.genes) > 0
            ]

            self.assertEqual(evolved.size(), population.size())
            self.assertGreater(len(non_elite_individuals), 0)
            self.assertGreater(len(scoreable_non_elite_individuals), 0)
            self.assertGreater(evolved_fittest_score, 0)
            self.assertTrue(fpl.validteam(evolved_fittest.genes[:15]))
            self.assertGreater(fpl.scoreteam(evolved_fittest.genes), 0)
        finally:
            random.setstate(random_state)


if __name__ == "__main__":
    unittest.main()
