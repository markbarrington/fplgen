import csv
import importlib
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CODE_DIR = PROJECT_ROOT / "code"
FIXTURE = PROJECT_ROOT / "tests" / "fixtures" / "fplreview_minimal.csv"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

fpl_module = importlib.import_module("fpl")
from fpl import fpl


class FplReviewImportTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.tempdir.name)
        self.original_data_file = fpl_module.data_file

        def temp_data_file(filename, for_write=False):
            if for_write:
                self.data_dir.mkdir(exist_ok=True)
            return self.data_dir / filename

        fpl_module.data_file = temp_data_file

    def tearDown(self):
        fpl_module.data_file = self.original_data_file
        self.tempdir.cleanup()
        fpl_module.players = []
        fpl_module.fixtures = []

    def test_import_fixture_maps_core_player_fields(self):
        players = fpl.load_fplreview_players(FIXTURE)

        self.assertEqual(len(players), 4)
        keeper = players[0]
        self.assertEqual(keeper["id"], 101)
        self.assertEqual(keeper["code"], 101)
        self.assertEqual(keeper["second_name"], "Alpha Keeper")
        self.assertEqual(keeper["team_name"], "Arsenal")
        self.assertEqual(keeper["element_type"], 1)
        self.assertEqual(keeper["type_name"], "Goalkeeper")
        self.assertEqual(keeper["now_cost"], 45)
        self.assertEqual(keeper["sellprice"], 44)
        self.assertEqual(keeper["status"], "a")

    def test_import_fixture_uses_gameweek_points_without_adjustment(self):
        players = fpl.load_fplreview_players(FIXTURE)
        midfielder = players[2]

        self.assertEqual(midfielder["1"], 6.2)
        self.assertEqual(midfielder["2"], 6.4)
        self.assertEqual(midfielder["6"], 6.6)
        self.assertEqual(midfielder["thisweekpoints"], 6.2)
        self.assertAlmostEqual(midfielder["lookaheadpoints"], 38.1)
        self.assertAlmostEqual(midfielder["ppg"], 38.1 / fpl_module.forecastweeks)

    def test_missing_required_column_fails_fast(self):
        with open(FIXTURE, newline="", encoding="utf-8") as fixture:
            rows = list(csv.DictReader(fixture))

        fieldnames = [field for field in rows[0].keys() if field != "Pos"]
        with self.assertRaisesRegex(ValueError, "Missing required fplreview columns: Pos"):
            fpl.map_fplreview_rows(rows, fieldnames)

    def test_missing_configured_gameweek_column_fails_fast(self):
        with open(FIXTURE, newline="", encoding="utf-8") as fixture:
            rows = list(csv.DictReader(fixture))

        fieldnames = [field for field in rows[0].keys() if field != "8_Pts"]
        with self.assertRaisesRegex(ValueError, "Missing required fplreview gameweek columns: 8_Pts"):
            fpl.map_fplreview_rows(rows, fieldnames)

    def test_getplayerdata_loads_fplreview_csv_and_writes_inspection_output(self):
        runtime_file = self.data_dir / "fplreview.csv"
        runtime_file.write_text(FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")

        fpl.getplayerdata()

        self.assertEqual(len(fpl_module.players), 4)
        self.assertEqual(fpl_module.players[1]["second_name"], "Beta Defender")
        self.assertEqual(fpl_module.players[1]["1"], 5.0)

        playerkeydata = self.data_dir / "playerkeydata"
        self.assertTrue(playerkeydata.exists())
        output = playerkeydata.read_text(encoding="utf-8-sig")
        self.assertIn("Beta Defender", output)
        self.assertIn(",5.0,4.8,4.7,4.9,5.1,5.2", output)

    def test_mapped_players_keep_existing_cost_and_availability_shape(self):
        players = fpl.load_fplreview_players(FIXTURE)

        self.assertEqual(fpl.teamvalue(players), 45 + 52 + 80 + 75)
        self.assertEqual(players[0]["sellprice"], 44)
        self.assertTrue(all(player["status"] == "a" for player in players))


if __name__ == "__main__":
    unittest.main()
