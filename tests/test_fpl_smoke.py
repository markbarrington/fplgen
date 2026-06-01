import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CODE_DIR = PROJECT_ROOT / "code"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from fpl import fpl
from paths import DATA_DIR, data_file


def player(player_id, team, element_type, cost=50):
    return {
        "id": player_id,
        "team": team,
        "team_name": "Team %s" % team,
        "element_type": element_type,
        "now_cost": cost,
    }


class FplSmokeTests(unittest.TestCase):
    def test_data_file_writes_to_data_directory(self):
        self.assertEqual(data_file("playerkeydata", for_write=True), DATA_DIR / "playerkeydata")

    def test_valid_team_accepts_legal_squad(self):
        team = [
            player(1, 1, 1),
            player(2, 2, 1),
            player(3, 3, 2),
            player(4, 4, 2),
            player(5, 5, 2),
            player(6, 6, 2),
            player(7, 7, 2),
            player(8, 8, 3),
            player(9, 9, 3),
            player(10, 10, 3),
            player(11, 11, 3),
            player(12, 12, 3),
            player(13, 13, 4),
            player(14, 14, 4),
            player(15, 15, 4),
        ]

        self.assertTrue(fpl.validteam(team))

    def test_valid_team_rejects_duplicate_player(self):
        duplicate = player(1, 1, 1)
        team = [duplicate, duplicate] + [player(i, i, 2, cost=1) for i in range(2, 15)]

        self.assertFalse(fpl.validteam(team))

    def test_valid_team_rejects_over_budget_squad(self):
        team = [player(i, i, 1, cost=100) for i in range(1, 16)]

        self.assertFalse(fpl.validteam(team))


if __name__ == "__main__":
    unittest.main()
