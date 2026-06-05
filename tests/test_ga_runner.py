import importlib
import io
import json
import random
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CODE_DIR = PROJECT_ROOT / "code"
FIXTURE = PROJECT_ROOT / "tests" / "fixtures" / "fplreview_golden.csv"
FPLKIWI_FIXTURE = PROJECT_ROOT / "tests" / "fixtures" / "fplkiwi_historical.csv"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

fpl_module = importlib.import_module("fpl")
ga_module = importlib.import_module("GA")
from generate_scenario import generate_scenario_data

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


class GARunnerTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.tempdir.name)
        self.original_data_file = fpl_module.data_file
        self.original_gameweek = fpl_module.gameweek
        self.original_forecastweeks = fpl_module.forecastweeks
        self.random_state = random.getstate()

        def temp_data_file(filename, for_write=False):
            if for_write:
                self.data_dir.mkdir(exist_ok=True)
            return self.data_dir / filename

        fpl_module.data_file = temp_data_file

    def tearDown(self):
        fpl_module.data_file = self.original_data_file
        fpl_module.gameweek = self.original_gameweek
        fpl_module.forecastweeks = self.original_forecastweeks
        fpl_module.players = []
        fpl_module.fixtures = []
        random.setstate(self.random_state)
        self.tempdir.cleanup()

    def test_parse_args_uses_current_defaults(self):
        options = ga_module.parse_args([])

        self.assertEqual(options.input, ga_module.DEFAULT_INPUT)
        self.assertEqual(options.population, 10000)
        self.assertEqual(options.generations, 300)
        self.assertIsNone(options.seed)
        self.assertEqual(options.gameweek, self.original_gameweek)
        self.assertEqual(options.forecastweeks, self.original_forecastweeks)

    def test_parse_args_accepts_runtime_controls(self):
        options = ga_module.parse_args(
            [
                "--input",
                str(FIXTURE),
                "--scenario",
                "scenario.json",
                "--population",
                "6",
                "--generations",
                "2",
                "--seed",
                "7",
                "--gameweek",
                "4",
                "--forecastweeks",
                "3",
            ]
        )

        self.assertEqual(options.input, FIXTURE)
        self.assertEqual(options.scenario, Path("scenario.json"))
        self.assertEqual(options.population, 6)
        self.assertEqual(options.generations, 2)
        self.assertEqual(options.seed, 7)
        self.assertEqual(options.gameweek, 4)
        self.assertEqual(options.forecastweeks, 3)

    def test_parse_args_rejects_invalid_numeric_controls(self):
        invalid_options = [
            ["--population", "0"],
            ["--generations", "0"],
            ["--gameweek", "0"],
            ["--forecastweeks", "0"],
        ]

        for args in invalid_options:
            with self.subTest(args=args):
                with self.assertRaises(SystemExit):
                    with redirect_stderr(io.StringIO()):
                        ga_module.parse_args(args)

    def test_runner_loads_custom_input_and_writes_inspection_output(self):
        scenario_path = self.write_scenario("scenario.json", gameweek=3)

        with redirect_stdout(io.StringIO()):
            result = ga_module.run(
                input_path=FIXTURE,
                scenario_path=scenario_path,
                population_size=6,
                generation_limit=1,
                seed=7,
                gameweek=3,
            )

        self.assertGreater(result["fittest_score"], 0)
        self.assertEqual(result["generation_count"], 1)
        self.assertGreater(len(fpl_module.players), 15)
        self.assertEqual(fpl_module.players[0]["id"], 201)
        self.assertTrue((self.data_dir / "playerkeydata").exists())

    def test_runner_seeded_short_run_is_reproducible(self):
        scenario_path = self.write_scenario("scenario.json", gameweek=3)

        with redirect_stdout(io.StringIO()):
            first = ga_module.run(
                input_path=FIXTURE,
                scenario_path=scenario_path,
                population_size=6,
                generation_limit=2,
                seed=7,
                gameweek=3,
            )
            second = ga_module.run(
                input_path=FIXTURE,
                scenario_path=scenario_path,
                population_size=6,
                generation_limit=2,
                seed=7,
                gameweek=3,
            )

        self.assertEqual(first["fittest_score"], second["fittest_score"])
        self.assertEqual(first["generation_count"], second["generation_count"])

    def test_runner_horizon_missing_columns_fails_before_population_creation(self):
        with self.assertRaisesRegex(ValueError, "Missing required fplreview gameweek columns: 9_Pts"):
            with redirect_stdout(io.StringIO()):
                ga_module.run(
                    input_path=FIXTURE,
                    population_size=6,
                    generation_limit=1,
                    seed=7,
                    gameweek=9,
                    forecastweeks=1,
                )

    def test_runner_defaults_do_not_inherit_prior_horizon_overrides(self):
        with redirect_stdout(io.StringIO()):
            ga_module.run(
                input_path=FIXTURE,
                population_size=6,
                generation_limit=1,
                seed=7,
                gameweek=4,
                forecastweeks=1,
                scenario_path=self.write_scenario("scenario-4.json", gameweek=4),
            )
            ga_module.run(
                input_path=FIXTURE,
                population_size=6,
                generation_limit=1,
                seed=7,
                scenario_path=self.write_scenario("scenario-3.json", gameweek=ga_module.DEFAULT_GAMEWEEK),
            )

        self.assertEqual(fpl_module.gameweek, ga_module.DEFAULT_GAMEWEEK)
        self.assertEqual(fpl_module.forecastweeks, ga_module.DEFAULT_FORECASTWEEKS)
        self.assertIn("6", fpl_module.players[0])

    def test_non_gw1_without_scenario_fails_before_population_creation(self):
        output = io.StringIO()
        with self.assertRaisesRegex(ValueError, "Scenario file is required"):
            with patch.object(ga_module, "Population") as population:
                with redirect_stdout(output):
                    ga_module.run(
                        input_path=FIXTURE,
                        population_size=6,
                        generation_limit=1,
                        seed=7,
                        gameweek=3,
                    )

        population.assert_not_called()
        self.assertNotIn("Creating intial population", output.getvalue())

    def test_non_gw1_with_valid_scenario_prints_context(self):
        scenario_path = self.write_scenario("scenario.json", gameweek=3)

        output = io.StringIO()
        with redirect_stdout(output):
            result = ga_module.run(
                input_path=FIXTURE,
                scenario_path=scenario_path,
                population_size=6,
                generation_limit=1,
                seed=7,
                gameweek=3,
            )

        self.assertEqual(result["scenario"].gameweek, 3)
        self.assertIn("Existing squad scenario", output.getvalue())
        self.assertIn("bank 0.7", output.getvalue())
        self.assertIn("saved free transfers 2", output.getvalue())

    def test_non_gw1_scenario_gameweek_mismatch_fails_before_population_creation(self):
        scenario_path = self.write_scenario("scenario.json", gameweek=4)
        output = io.StringIO()

        with self.assertRaisesRegex(ValueError, "does not match configured gameweek"):
            with patch.object(ga_module, "Population") as population:
                with redirect_stdout(output):
                    ga_module.run(
                        input_path=FIXTURE,
                        scenario_path=scenario_path,
                        population_size=6,
                        generation_limit=1,
                        seed=7,
                        gameweek=3,
                    )

        population.assert_not_called()
        self.assertNotIn("Creating intial population", output.getvalue())

    def write_scenario(self, filename, gameweek=3):
        path = self.data_dir / filename
        path.write_text(
            json.dumps(
                {
                    "gameweek": gameweek,
                    "bank": 0.7,
                    "saved_free_transfers": 2,
                    "current_squad": KNOWN_SQUAD_IDS,
                }
            ),
            encoding="utf-8",
        )
        return path

    def test_runner_completes_with_fplkiwi_historical_fixture(self):
        scenario_path = self.write_generated_scenario(
            "fplkiwi-scenario.json",
            input_path=FPLKIWI_FIXTURE,
            gameweek=18,
            forecastweeks=6,
        )

        with redirect_stdout(io.StringIO()):
            result = ga_module.run(
                input_path=FPLKIWI_FIXTURE,
                scenario_path=scenario_path,
                population_size=10,
                generation_limit=1,
                seed=1,
                gameweek=18,
                forecastweeks=6,
            )

        self.assertGreater(result["fittest_score"], 0)
        self.assertEqual(result["generation_count"], 1)
        self.assertEqual(len(fpl_module.players), 461)
        self.assertEqual(fpl_module.gameweek, 18)
        self.assertEqual(fpl_module.forecastweeks, 6)
        self.assertEqual(fpl_module.players[0]["id"], 113)
        self.assertAlmostEqual(fpl_module.players[0]["6"], 3.309606969)
        self.assertTrue((self.data_dir / "playerkeydata").exists())

    def write_generated_scenario(self, filename, input_path, gameweek, forecastweeks):
        path = self.data_dir / filename
        path.write_text(
            json.dumps(
                generate_scenario_data(
                    input_path,
                    gameweek=gameweek,
                    forecastweeks=forecastweeks,
                    seed=1,
                )
            ),
            encoding="utf-8",
        )
        return path


if __name__ == "__main__":
    unittest.main()
