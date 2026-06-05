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
from projections import (
    format_playerkeydata_lines,
    normalize_fplreview_rows,
    prepare_scorer_players,
    read_fplreview_csv,
)


class FplReviewImportTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.tempdir.name)
        self.original_data_file = fpl_module.data_file
        self.original_teamid = dict(fpl_module.teamid)

        def temp_data_file(filename, for_write=False):
            if for_write:
                self.data_dir.mkdir(exist_ok=True)
            return self.data_dir / filename

        fpl_module.data_file = temp_data_file

    def tearDown(self):
        fpl_module.data_file = self.original_data_file
        fpl_module.teamid = self.original_teamid
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

    def test_normalization_preserves_projection_values_without_writing_inspection_output(self):
        source = read_fplreview_csv(FIXTURE)

        normalized, updated_teamid = normalize_fplreview_rows(
            source.rows,
            source.fieldnames,
            fpl_module.gameweek,
            fpl_module.forecastweeks,
            fpl_module.teamid,
        )
        players = prepare_scorer_players(
            normalized,
            fpl_module.forecastweeks,
            fpl_module.playertypes,
        )
        midfielder = players[2]

        self.assertFalse((self.data_dir / "playerkeydata").exists())
        self.assertEqual(updated_teamid, fpl_module.teamid)
        self.assertEqual(normalized[2].player_id, 103)
        self.assertEqual(normalized[2].team_name, "Man City")
        self.assertEqual(normalized[2].element_type, 3)
        self.assertEqual(normalized[2].now_cost, 80)
        self.assertEqual(normalized[2].sellprice, 79)
        self.assertEqual(normalized[2].weekly_points[1], 6.2)
        self.assertEqual(midfielder["1"], 6.2)
        self.assertEqual(midfielder["thisweekpoints"], 6.2)
        self.assertAlmostEqual(midfielder["lookaheadpoints"], 38.1)

    def test_normalization_with_new_teams_keeps_stable_local_team_map(self):
        rows = [
            {
                "Pos": "MID",
                "ID": "999",
                "Name": "New Team Midfielder",
                "BV": "5.5",
                "SV": "5.4",
                "Team": "New Club",
                "3_Pts": "1.1",
                "4_Pts": "1.2",
                "5_Pts": "1.3",
                "6_Pts": "1.4",
                "7_Pts": "1.5",
                "8_Pts": "1.6",
            },
            {
                "Pos": "DEF",
                "ID": "1000",
                "Name": "New Team Defender",
                "BV": "4.5",
                "SV": "4.4",
                "Team": "New Club",
                "3_Pts": "2.1",
                "4_Pts": "2.2",
                "5_Pts": "2.3",
                "6_Pts": "2.4",
                "7_Pts": "2.5",
                "8_Pts": "2.6",
            },
            {
                "Pos": "FWD",
                "ID": "1001",
                "Name": "Other New Forward",
                "BV": "6.5",
                "SV": "6.4",
                "Team": "Other New Club",
                "3_Pts": "3.1",
                "4_Pts": "3.2",
                "5_Pts": "3.3",
                "6_Pts": "3.4",
                "7_Pts": "3.5",
                "8_Pts": "3.6",
            }
        ]
        fieldnames = list(rows[0].keys())

        first, first_teamid = normalize_fplreview_rows(
            rows,
            fieldnames,
            fpl_module.gameweek,
            fpl_module.forecastweeks,
            fpl_module.teamid,
        )
        second, second_teamid = normalize_fplreview_rows(
            rows,
            fieldnames,
            fpl_module.gameweek,
            fpl_module.forecastweeks,
            fpl_module.teamid,
        )

        self.assertNotIn("New Club", fpl_module.teamid.values())
        self.assertNotIn("Other New Club", fpl_module.teamid.values())
        self.assertEqual(first[0].team, first[1].team)
        self.assertNotEqual(first[0].team, first[2].team)
        self.assertEqual(
            [projection.team for projection in first],
            [projection.team for projection in second],
        )
        self.assertEqual(first_teamid, second_teamid)
        self.assertIn("New Club", first_teamid.values())
        self.assertIn("Other New Club", first_teamid.values())

    def test_source_import_rejects_csv_without_header_row(self):
        with tempfile.TemporaryDirectory() as tempdir:
            source_path = Path(tempdir) / "empty.csv"
            source_path.write_text("", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "fplreview CSV has no header row"):
                read_fplreview_csv(source_path)

            self.assertFalse((self.data_dir / "playerkeydata").exists())

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

    def test_inspection_output_formats_loaded_projection_values(self):
        players = fpl.load_fplreview_players(FIXTURE)

        lines = format_playerkeydata_lines(
            players,
            fpl_module.forecastweeks,
            fpl_module.playertype,
        )

        self.assertEqual(
            lines[1].split(","),
            [
                "Beta Defender",
                "29.7",
                "0",
                "29.7",
                "52",
                "Chelsea",
                "Defender",
                "29.7",
                "5.0",
                str(29.7 / fpl_module.forecastweeks),
                "5.0",
                "4.8",
                "4.7",
                "4.9",
                "5.1",
                "5.2",
            ],
        )

    def test_inspection_output_uses_active_forecast_horizon(self):
        players = fpl.load_fplreview_players(FIXTURE)

        lines = format_playerkeydata_lines(
            players,
            2,
            fpl_module.playertype,
        )

        self.assertEqual(lines[1].split(",")[-2:], ["5.0", "4.8"])
        self.assertEqual(len(lines[1].split(",")), 12)

    def test_mapped_players_keep_existing_cost_and_availability_shape(self):
        players = fpl.load_fplreview_players(FIXTURE)

        self.assertEqual(fpl.teamvalue(players), 45 + 52 + 80 + 75)
        self.assertEqual(players[0]["sellprice"], 44)
        self.assertTrue(all(player["status"] == "a" for player in players))


if __name__ == "__main__":
    unittest.main()
