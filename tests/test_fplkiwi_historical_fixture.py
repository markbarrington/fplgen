import importlib
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CODE_DIR = PROJECT_ROOT / "code"
FIXTURE_DIR = PROJECT_ROOT / "tests" / "fixtures"
FIXTURE = FIXTURE_DIR / "fplkiwi_historical.csv"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))
if str(FIXTURE_DIR) not in sys.path:
    sys.path.insert(0, str(FIXTURE_DIR))

fpl_module = importlib.import_module("fpl")
from fpl import fpl
from convert_fplkiwi_fixture import convert_file


KNOWN_SQUAD_IDS = [
    116,
    361,
    10019,
    473,
    316,
    366,
    37,
    92,
    219,
    403,
    196,
    52,
    490,
    538,
    82,
]


class FplKiwiHistoricalFixtureTests(unittest.TestCase):
    def setUp(self):
        self.original_gameweek = fpl_module.gameweek
        self.original_forecastweeks = fpl_module.forecastweeks
        self.original_teamid = dict(fpl_module.teamid)
        fpl_module.gameweek = 18
        fpl_module.forecastweeks = 6

    def tearDown(self):
        fpl_module.gameweek = self.original_gameweek
        fpl_module.forecastweeks = self.original_forecastweeks
        fpl_module.teamid = self.original_teamid
        fpl_module.players = []
        fpl_module.fixtures = []

    def test_converter_filters_zero_ids_and_writes_fplreview_columns(self):
        source = """ID,Name,Pos,Price,Team,xPts GW18-38,Mins/95,18,19,Pts,18,19
0,Invalid Youth,MID,3.0,ARS,1.0,,10,10,,1.1,1.2
113,Raya,GK,4.9,ARS,8.0,,90,90,,2.946007565,4.089056194
"""
        with tempfile.TemporaryDirectory() as tempdir:
            source_path = Path(tempdir) / "kiwi.csv"
            output_path = Path(tempdir) / "converted.csv"
            source_path.write_text(source, encoding="utf-8")

            stats = convert_file(source_path, output_path, start_week=18, forecast_weeks=2)

            self.assertEqual(stats["rows_read"], 2)
            self.assertEqual(stats["rows_written"], 1)
            self.assertEqual(stats["skipped_invalid_ids"], 1)
            self.assertEqual(
                output_path.read_text(encoding="utf-8").splitlines(),
                [
                    "Pos,ID,Name,BV,SV,Team,18_Pts,19_Pts",
                    "GKP,113,Raya,4.9,4.9,ARS,2.946007565,4.089056194",
                ],
            )

    def test_converter_fails_for_missing_required_source_columns(self):
        source = """ID,Name,Price,Team,Pts,18
113,Raya,4.9,ARS,,2.946007565
"""
        with tempfile.TemporaryDirectory() as tempdir:
            source_path = Path(tempdir) / "kiwi.csv"
            output_path = Path(tempdir) / "converted.csv"
            source_path.write_text(source, encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "Missing theFPLkiwi column: Pos"):
                convert_file(source_path, output_path, start_week=18, forecast_weeks=1)

            self.assertFalse(output_path.exists())

    def test_converter_fails_for_missing_points_section_or_week(self):
        missing_points_section = """ID,Name,Pos,Price,Team,18
113,Raya,GK,4.9,ARS,2.946007565
"""
        missing_week = """ID,Name,Pos,Price,Team,Pts,18
113,Raya,GK,4.9,ARS,,2.946007565
"""
        with tempfile.TemporaryDirectory() as tempdir:
            source_path = Path(tempdir) / "kiwi.csv"
            output_path = Path(tempdir) / "converted.csv"

            source_path.write_text(missing_points_section, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Missing theFPLkiwi projected points section: Pts"):
                convert_file(source_path, output_path, start_week=18, forecast_weeks=1)
            self.assertFalse(output_path.exists())

            source_path.write_text(missing_week, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Missing theFPLkiwi points column: 19"):
                convert_file(source_path, output_path, start_week=18, forecast_weeks=2)
            self.assertFalse(output_path.exists())

    def test_converter_fails_for_unknown_positions_and_blank_points(self):
        unknown_position = """ID,Name,Pos,Price,Team,Pts,18
113,Raya,WING,4.9,ARS,,2.946007565
"""
        blank_points = """ID,Name,Pos,Price,Team,Pts,18
113,Raya,GK,4.9,ARS,,
"""
        with tempfile.TemporaryDirectory() as tempdir:
            source_path = Path(tempdir) / "kiwi.csv"
            output_path = Path(tempdir) / "converted.csv"

            source_path.write_text(unknown_position, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Unknown theFPLkiwi position: WING"):
                convert_file(source_path, output_path, start_week=18, forecast_weeks=1)
            self.assertFalse(output_path.exists())

            source_path.write_text(blank_points, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Blank theFPLkiwi points value for ID 113 week 18"):
                convert_file(source_path, output_path, start_week=18, forecast_weeks=1)
            self.assertFalse(output_path.exists())

    def test_historical_fixture_imports_with_realistic_projection_row_coverage(self):
        players = fpl.load_fplreview_players(FIXTURE)

        self.assertEqual(len(players), 461)
        self.assertTrue(all(player["id"] > 0 for player in players))
        self.assertEqual({player["element_type"] for player in players}, {1, 2, 3, 4})
        self.assertEqual(len({player["team_name"] for player in players}), 20)

        counts = Counter(player["element_type"] for player in players)
        self.assertGreaterEqual(counts[1], 20)
        self.assertGreaterEqual(counts[2], 100)
        self.assertGreaterEqual(counts[3], 150)
        self.assertGreaterEqual(counts[4], 40)

    def test_historical_fixture_preserves_representative_converted_values(self):
        players = {player["id"]: player for player in fpl.load_fplreview_players(FIXTURE)}
        raya = players[113]

        self.assertEqual(raya["second_name"], "Raya")
        self.assertEqual(raya["team_name"], "ARS")
        self.assertEqual(raya["element_type"], 1)
        self.assertEqual(raya["now_cost"], 49)
        self.assertEqual(raya["sellprice"], 49)
        self.assertAlmostEqual(raya["1"], 2.946007565)
        self.assertAlmostEqual(raya["6"], 3.309606969)
        self.assertAlmostEqual(raya["lookaheadpoints"], 23.060550321)

    def test_historical_fixture_can_score_a_valid_squad_without_benchmark_assertions(self):
        players = {player["id"]: player for player in fpl.load_fplreview_players(FIXTURE)}
        team = [players[player_id] for player_id in KNOWN_SQUAD_IDS]
        team.append([0, 0, 0, 0])
        team.append([0, 0, 0, 0])

        self.assertEqual(Counter(player["element_type"] for player in team[:15]), {1: 2, 2: 5, 3: 5, 4: 3})
        self.assertLessEqual(fpl.teamvalue(team), fpl_module.budget)
        self.assertTrue(fpl.validteam(team))
        self.assertGreater(fpl.scoreteam(team), 0)


if __name__ == "__main__":
    unittest.main()
