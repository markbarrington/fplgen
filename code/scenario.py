import json
from collections import Counter
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

import fpl as fpl_module


@dataclass(frozen=True)
class Scenario:
    gameweek: int
    bank: int
    saved_free_transfers: int
    current_squad: list
    source: str = None


def validate_scenario_file(path, players, configured_gameweek):
    try:
        with open(path, "r", encoding="utf-8") as scenario_file:
            data = json.load(scenario_file)
    except json.JSONDecodeError as error:
        raise ValueError("Invalid scenario JSON: %s" % error) from error

    return validate_scenario_data(
        data,
        players,
        configured_gameweek=configured_gameweek,
        source=str(path),
    )


def validate_scenario_data(data, players, configured_gameweek, source=None):
    if not isinstance(data, dict):
        raise ValueError("Scenario JSON must be an object")

    required = ["gameweek", "bank", "saved_free_transfers", "current_squad"]
    missing = [field for field in required if field not in data]
    if missing:
        raise ValueError("Missing scenario fields: %s" % ", ".join(missing))

    scenario_gameweek = _positive_int(data["gameweek"], "gameweek")
    if scenario_gameweek != configured_gameweek:
        raise ValueError(
            "Scenario gameweek %s does not match configured gameweek %s"
            % (scenario_gameweek, configured_gameweek)
        )

    bank = _bank_to_tenths(data["bank"])
    saved_free_transfers = _saved_free_transfers(data["saved_free_transfers"])
    current_squad = _resolve_current_squad(data["current_squad"], players)
    validate_current_squad(current_squad)

    return Scenario(
        gameweek=scenario_gameweek,
        bank=bank,
        saved_free_transfers=saved_free_transfers,
        current_squad=current_squad,
        source=source,
    )


def validate_current_squad(squad):
    if len(squad) != fpl_module.squadsize:
        raise ValueError("current_squad must contain exactly 15 player IDs")

    ids = [player["id"] for player in squad]
    duplicates = sorted(player_id for player_id, count in Counter(ids).items() if count > 1)
    if duplicates:
        raise ValueError("current_squad contains duplicate player IDs: %s" % duplicates)

    club_counts = Counter(player["team"] for player in squad)
    overloaded = sorted(club for club, count in club_counts.items() if count > fpl_module.maxperteam)
    if overloaded:
        raise ValueError("current_squad has more than 3 players from one club: %s" % overloaded)

    position_counts = Counter(player["element_type"] for player in squad)
    expected = {idx + 1: count for idx, count in enumerate(fpl_module.squadcount)}
    if dict(position_counts) != expected:
        raise ValueError("current_squad has invalid position counts: %s" % dict(position_counts))

    return True


def _positive_int(value, field_name):
    if isinstance(value, bool):
        raise ValueError("%s must be a positive integer" % field_name)
    try:
        number = int(value)
    except (TypeError, ValueError) as error:
        raise ValueError("%s must be a positive integer" % field_name) from error
    if number <= 0 or str(value) != str(number):
        raise ValueError("%s must be a positive integer" % field_name)
    return number


def _bank_to_tenths(value):
    try:
        decimal_value = Decimal(str(value))
    except (InvalidOperation, ValueError) as error:
        raise ValueError("bank must be a non-negative decimal value") from error

    if decimal_value < 0:
        raise ValueError("bank must be a non-negative decimal value")

    tenths = decimal_value * Decimal("10")
    if tenths != tenths.to_integral_value():
        raise ValueError("bank must use one decimal place")

    return int(tenths)


def _saved_free_transfers(value):
    transfers = _positive_int(value, "saved_free_transfers")
    if transfers > 5:
        raise ValueError("saved_free_transfers must be between 1 and 5")
    return transfers


def _resolve_current_squad(current_squad, players):
    if not isinstance(current_squad, list):
        raise ValueError("current_squad must be a list of player IDs")

    player_ids = []
    for value in current_squad:
        if isinstance(value, bool):
            raise ValueError("current_squad must contain integer player IDs")
        try:
            player_id = int(value)
        except (TypeError, ValueError) as error:
            raise ValueError("current_squad must contain integer player IDs") from error
        if str(value) != str(player_id):
            raise ValueError("current_squad must contain integer player IDs")
        player_ids.append(player_id)

    by_id = {player["id"]: player for player in players}
    missing = [player_id for player_id in player_ids if player_id not in by_id]
    if missing:
        raise ValueError("current_squad player IDs not found in projections: %s" % missing)

    return [by_id[player_id] for player_id in player_ids]
