import json
import copy
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CODE_DIR = PROJECT_ROOT / "code"
FIXTURE = PROJECT_ROOT / "tests" / "fixtures" / "fplreview_golden.csv"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from fpl import fpl
from scenario import validate_scenario_file, validate_scenario_data


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


class ScenarioValidationTests(unittest.TestCase):
    def setUp(self):
        self.players = fpl.load_fplreview_players(FIXTURE)
        self.valid_data = {
            "gameweek": 3,
            "bank": 0.7,
            "saved_free_transfers": 2,
            "current_squad": KNOWN_SQUAD_IDS,
        }

    def test_valid_scenario_resolves_players_and_converts_bank(self):
        scenario = validate_scenario_data(self.valid_data, self.players, configured_gameweek=3)

        self.assertEqual(scenario.gameweek, 3)
        self.assertEqual(scenario.bank, 7)
        self.assertEqual(scenario.saved_free_transfers, 2)
        self.assertEqual([player["id"] for player in scenario.current_squad], KNOWN_SQUAD_IDS)

    def test_duplicate_ids_fail(self):
        data = dict(self.valid_data)
        data["current_squad"] = [201, 201] + KNOWN_SQUAD_IDS[2:]

        with self.assertRaisesRegex(ValueError, "duplicate player IDs"):
            validate_scenario_data(data, self.players, configured_gameweek=3)

    def test_missing_projection_id_fails(self):
        data = dict(self.valid_data)
        data["current_squad"] = KNOWN_SQUAD_IDS[:-1] + [9999]

        with self.assertRaisesRegex(ValueError, "not found in projections: \\[9999\\]"):
            validate_scenario_data(data, self.players, configured_gameweek=3)

    def test_bad_squad_shape_fails(self):
        data = dict(self.valid_data)
        data["current_squad"] = KNOWN_SQUAD_IDS[:-1] + [203]

        with self.assertRaisesRegex(ValueError, "position counts"):
            validate_scenario_data(data, self.players, configured_gameweek=3)

    def test_wrong_squad_length_fails(self):
        for squad in [KNOWN_SQUAD_IDS[:-1], KNOWN_SQUAD_IDS + [203]]:
            with self.subTest(length=len(squad)):
                data = dict(self.valid_data)
                data["current_squad"] = squad

                with self.assertRaisesRegex(ValueError, "exactly 15 player IDs"):
                    validate_scenario_data(data, self.players, configured_gameweek=3)

    def test_too_many_from_one_club_fails(self):
        data = dict(self.valid_data)
        players = copy.deepcopy(self.players)
        for player in players:
            if player["id"] in [204, 205, 206]:
                player["team"] = 1
                player["team_name"] = "Arsenal"

        with self.assertRaisesRegex(ValueError, "more than 3 players"):
            validate_scenario_data(data, players, configured_gameweek=3)

    def test_gameweek_mismatch_fails(self):
        data = dict(self.valid_data)
        data["gameweek"] = 4

        with self.assertRaisesRegex(ValueError, "gameweek.*does not match"):
            validate_scenario_data(data, self.players, configured_gameweek=3)

    def test_malformed_values_fail(self):
        bad_values = [
            ("bank", "lots", "bank"),
            ("bank", -0.1, "bank"),
            ("saved_free_transfers", "two", "saved_free_transfers"),
            ("saved_free_transfers", 6, "saved_free_transfers"),
            ("gameweek", 0, "gameweek"),
        ]

        for field, value, message in bad_values:
            with self.subTest(field=field, value=value):
                data = dict(self.valid_data)
                data[field] = value
                with self.assertRaisesRegex(ValueError, message):
                    validate_scenario_data(data, self.players, configured_gameweek=3)

    def test_malformed_json_and_missing_fields_fail(self):
        with tempfile.TemporaryDirectory() as tempdir:
            bad_json = Path(tempdir) / "bad.json"
            bad_json.write_text("{not-json", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "Invalid scenario JSON"):
                validate_scenario_file(bad_json, self.players, configured_gameweek=3)

            missing = Path(tempdir) / "missing.json"
            missing.write_text(json.dumps({"gameweek": 3}), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "Missing scenario fields"):
                validate_scenario_file(missing, self.players, configured_gameweek=3)


if __name__ == "__main__":
    unittest.main()
