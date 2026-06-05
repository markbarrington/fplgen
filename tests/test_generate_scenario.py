import json
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CODE_DIR = PROJECT_ROOT / "code"
FIXTURE = PROJECT_ROOT / "tests" / "fixtures" / "fplreview_golden.csv"
TEMPLATE = PROJECT_ROOT / "examples" / "scenario_template.json"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from fpl import fpl
from generate_scenario import generate_scenario_data, main, select_legal_squad
from scenario import validate_current_squad, validate_scenario_data


class GenerateScenarioTests(unittest.TestCase):
    def test_generator_is_deterministic_and_validates(self):
        first = generate_scenario_data(
            FIXTURE,
            gameweek=3,
            bank=0.7,
            saved_free_transfers=2,
            seed=7,
        )
        second = generate_scenario_data(
            FIXTURE,
            gameweek=3,
            bank=0.7,
            saved_free_transfers=2,
            seed=7,
        )
        players = fpl.load_fplreview_players(FIXTURE)

        self.assertEqual(first, second)
        scenario = validate_scenario_data(first, players, configured_gameweek=3)
        self.assertEqual(scenario.bank, 7)
        self.assertEqual(scenario.saved_free_transfers, 2)

    def test_generator_seed_controls_selection(self):
        first = generate_scenario_data(FIXTURE, gameweek=3, seed=1)
        second = generate_scenario_data(FIXTURE, gameweek=3, seed=2)

        self.assertNotEqual(first["current_squad"], second["current_squad"])

    def test_generator_cli_writes_json(self):
        with tempfile.TemporaryDirectory() as tempdir:
            output = Path(tempdir) / "scenario.json"

            with redirect_stdout(io.StringIO()):
                main(
                    [
                        "--input",
                        str(FIXTURE),
                        "--output",
                        str(output),
                        "--gameweek",
                        "3",
                        "--bank",
                        "0.7",
                        "--saved-free-transfers",
                        "2",
                        "--seed",
                        "7",
                    ]
                )

            data = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(data["gameweek"], 3)
            self.assertEqual(data["bank"], 0.7)
            self.assertEqual(data["saved_free_transfers"], 2)
            self.assertEqual(len(data["current_squad"]), 15)

    def test_generator_fails_when_squad_cannot_be_built(self):
        with self.assertRaisesRegex(ValueError, "cannot produce a legal 15-player squad"):
            generate_scenario_data(
                PROJECT_ROOT / "tests" / "fixtures" / "fplreview_minimal.csv",
                gameweek=3,
                forecastweeks=2,
            )

    def test_generator_backtracks_to_find_a_legal_squad(self):
        players = []
        player_id = 1000

        def add_player(element_type, team, points):
            nonlocal player_id
            player = {
                "id": player_id,
                "team": team,
                "team_name": "Team %s" % team,
                "element_type": element_type,
                "now_cost": 50,
                "lookaheadpoints": points,
                "status": "a",
            }
            players.append(player)
            player_id += 1

        add_player(1, 1, 100)
        add_player(1, 2, 10)
        add_player(1, 3, 9)
        for team in [4, 5, 6, 7, 8]:
            add_player(2, team, 10)
        for team in [9, 10, 11, 12, 13]:
            add_player(3, team, 10)
        for _ in range(3):
            add_player(4, 1, 10)

        squad = select_legal_squad(players)

        validate_current_squad(squad)
        self.assertNotIn(players[0], squad)

    def test_template_is_valid_json_with_required_fields(self):
        data = json.loads(TEMPLATE.read_text(encoding="utf-8"))

        self.assertEqual(
            sorted(data.keys()),
            ["bank", "current_squad", "gameweek", "saved_free_transfers"],
        )
        self.assertEqual(len(data["current_squad"]), 15)
        players = fpl.load_fplreview_players(FIXTURE)
        validate_scenario_data(data, players, configured_gameweek=data["gameweek"])


if __name__ == "__main__":
    unittest.main()
