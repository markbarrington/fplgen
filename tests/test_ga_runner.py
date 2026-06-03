import importlib
import io
import random
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CODE_DIR = PROJECT_ROOT / "code"
FIXTURE = PROJECT_ROOT / "tests" / "fixtures" / "fplreview_golden.csv"
FPLKIWI_FIXTURE = PROJECT_ROOT / "tests" / "fixtures" / "fplkiwi_historical.csv"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

fpl_module = importlib.import_module("fpl")
ga_module = importlib.import_module("GA")


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
        with redirect_stdout(io.StringIO()):
            result = ga_module.run(
                input_path=FIXTURE,
                population_size=6,
                generation_limit=1,
                seed=7,
            )

        self.assertGreater(result["fittest_score"], 0)
        self.assertEqual(result["generation_count"], 1)
        self.assertGreater(len(fpl_module.players), 15)
        self.assertEqual(fpl_module.players[0]["id"], 201)
        self.assertTrue((self.data_dir / "playerkeydata").exists())

    def test_runner_seeded_short_run_is_reproducible(self):
        with redirect_stdout(io.StringIO()):
            first = ga_module.run(
                input_path=FIXTURE,
                population_size=6,
                generation_limit=2,
                seed=7,
            )
            second = ga_module.run(
                input_path=FIXTURE,
                population_size=6,
                generation_limit=2,
                seed=7,
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
            )
            ga_module.run(
                input_path=FIXTURE,
                population_size=6,
                generation_limit=1,
                seed=7,
            )

        self.assertEqual(fpl_module.gameweek, ga_module.DEFAULT_GAMEWEEK)
        self.assertEqual(fpl_module.forecastweeks, ga_module.DEFAULT_FORECASTWEEKS)
        self.assertIn("6", fpl_module.players[0])

    def test_runner_completes_with_fplkiwi_historical_fixture(self):
        with redirect_stdout(io.StringIO()):
            result = ga_module.run(
                input_path=FPLKIWI_FIXTURE,
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


if __name__ == "__main__":
    unittest.main()
