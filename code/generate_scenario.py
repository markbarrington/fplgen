#!/usr/bin/env python3
import argparse
import json
import random
from collections import Counter
from pathlib import Path

import fpl as fpl_module
from fpl import fpl
from scenario import validate_scenario_data


def positive_int(value):
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def non_negative_decimal(value):
    number = float(value)
    if number < 0:
        raise argparse.ArgumentTypeError("must be non-negative")
    return number


def generate_scenario_data(
    input_path,
    gameweek,
    forecastweeks=None,
    bank=0.0,
    saved_free_transfers=1,
    seed=None,
):
    original_gameweek = fpl_module.gameweek
    original_forecastweeks = fpl_module.forecastweeks
    try:
        fpl_module.gameweek = gameweek
        if forecastweeks is not None:
            fpl_module.forecastweeks = forecastweeks
        players = fpl.load_fplreview_players(input_path)
    finally:
        fpl_module.gameweek = original_gameweek
        fpl_module.forecastweeks = original_forecastweeks

    squad = select_legal_squad(players, seed=seed)
    data = {
        "gameweek": gameweek,
        "bank": bank,
        "saved_free_transfers": saved_free_transfers,
        "current_squad": [player["id"] for player in squad],
    }
    validate_scenario_data(data, players, configured_gameweek=gameweek)
    return data


def select_legal_squad(players, seed=None):
    candidates = [player for player in players if player.get("status") == "a"]
    candidates = sorted(
        candidates,
        key=lambda item: (-item["lookaheadpoints"], item["now_cost"], item["id"]),
    )
    if seed is not None:
        random.Random(seed).shuffle(candidates)

    by_position = {}
    for player in candidates:
        by_position.setdefault(player["element_type"], []).append(player)

    positions = []
    for element_type, required_count in enumerate(fpl_module.squadcount, start=1):
        positions.extend([element_type] * required_count)

    selected = _select_squad(positions, by_position, [], Counter(), set())
    if selected is None:
        raise ValueError("Projection input cannot produce a legal 15-player squad")
    return selected


def _select_squad(positions, by_position, selected, club_counts, selected_ids):
    if len(selected) == len(positions):
        return selected

    element_type = positions[len(selected)]
    for player in by_position.get(element_type, []):
        if player["id"] in selected_ids:
            continue
        if club_counts[player["team"]] >= fpl_module.maxperteam:
            continue

        next_counts = club_counts.copy()
        next_counts[player["team"]] += 1
        result = _select_squad(
            positions,
            by_position,
            selected + [player],
            next_counts,
            selected_ids | {player["id"]},
        )
        if result is not None:
            return result

    return None


def write_scenario(data, output_path):
    output = json.dumps(data, indent=2, sort_keys=True)
    output_path = Path(output_path)
    output_path.write_text(output + "\n", encoding="utf-8")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Generate a valid test/demo existing-squad scenario from fplreview projections."
    )
    parser.add_argument("--input", type=Path, required=True, help="Path to a fplreview CSV export.")
    parser.add_argument("--output", type=Path, required=True, help="Path to write scenario JSON.")
    parser.add_argument("--gameweek", type=positive_int, required=True, help="Scenario gameweek.")
    parser.add_argument(
        "--forecastweeks",
        type=positive_int,
        default=None,
        help="Number of gameweeks to load from the fplreview export.",
    )
    parser.add_argument("--bank", type=non_negative_decimal, default=0.0)
    parser.add_argument("--saved-free-transfers", type=positive_int, default=1)
    parser.add_argument("--seed", type=int, default=None)
    return parser.parse_args(argv)


def main(argv=None):
    options = parse_args(argv)
    data = generate_scenario_data(
        options.input,
        gameweek=options.gameweek,
        forecastweeks=options.forecastweeks,
        bank=options.bank,
        saved_free_transfers=options.saved_free_transfers,
        seed=options.seed,
    )
    write_scenario(data, options.output)
    print("Wrote scenario: %s" % options.output)


if __name__ == "__main__":
    main()
