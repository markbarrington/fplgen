#!/usr/bin/env python3
"""Convert theFPLkiwi projection CSVs to FPLgen's fplreview fixture shape."""

import argparse
import csv
from collections import Counter
from pathlib import Path


CORE_COLUMNS = ["ID", "Name", "Pos", "Price", "Team"]
POSITION_MAP = {
    "GK": "GKP",
    "GKP": "GKP",
    "DEF": "DEF",
    "MID": "MID",
    "FWD": "FWD",
}


def positive_int(value):
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return parsed


def find_points_columns(header, start_week, forecast_weeks):
    try:
        points_marker = header.index("Pts")
    except ValueError as exc:
        raise ValueError("Missing theFPLkiwi projected points section: Pts") from exc

    columns = {}
    wanted = [str(week) for week in range(start_week, start_week + forecast_weeks)]
    for wanted_week in wanted:
        try:
            columns[wanted_week] = header.index(wanted_week, points_marker + 1)
        except ValueError as exc:
            raise ValueError("Missing theFPLkiwi points column: %s" % wanted_week) from exc
    return columns


def valid_fpl_id(value):
    try:
        return int(value) > 0
    except (TypeError, ValueError):
        return False


def row_value(row, index, column_name):
    try:
        return row[index]
    except IndexError as exc:
        raise ValueError("Missing value for theFPLkiwi column: %s" % column_name) from exc


def convert_rows(rows, header, start_week=18, forecast_weeks=6):
    for column in CORE_COLUMNS:
        if column not in header:
            raise ValueError("Missing theFPLkiwi column: %s" % column)

    point_columns = find_points_columns(header, start_week, forecast_weeks)
    indexes = {column: header.index(column) for column in CORE_COLUMNS}
    output_header = ["Pos", "ID", "Name", "BV", "SV", "Team"]
    output_header.extend("%s_Pts" % week for week in range(start_week, start_week + forecast_weeks))

    converted = []
    skipped_invalid_ids = 0
    for row in rows:
        player_id = row_value(row, indexes["ID"], "ID").strip()
        if not valid_fpl_id(player_id):
            skipped_invalid_ids += 1
            continue

        position = POSITION_MAP.get(row_value(row, indexes["Pos"], "Pos").strip().upper())
        if position is None:
            raise ValueError("Unknown theFPLkiwi position: %s" % row_value(row, indexes["Pos"], "Pos"))

        price = row_value(row, indexes["Price"], "Price").strip()
        output_row = {
            "Pos": position,
            "ID": str(int(player_id)),
            "Name": row_value(row, indexes["Name"], "Name").strip(),
            "BV": price,
            "SV": price,
            "Team": row_value(row, indexes["Team"], "Team").strip(),
        }
        for week, column_index in point_columns.items():
            points = row_value(row, column_index, "%s points" % week).strip()
            if points == "":
                raise ValueError(
                    "Blank theFPLkiwi points value for ID %s week %s" % (player_id, week)
                )
            output_row["%s_Pts" % week] = points
        converted.append(output_row)

    stats = {
        "rows_read": len(rows),
        "rows_written": len(converted),
        "skipped_invalid_ids": skipped_invalid_ids,
        "teams": len({row["Team"] for row in converted}),
        "positions": dict(sorted(Counter(row["Pos"] for row in converted).items())),
        "weeks": list(range(start_week, start_week + forecast_weeks)),
    }
    return output_header, converted, stats


def convert_file(source, output, start_week=18, forecast_weeks=6):
    with Path(source).open(newline="", encoding="utf-8-sig") as source_file:
        reader = csv.reader(source_file)
        header = next(reader, None)
        if header is None:
            raise ValueError("theFPLkiwi CSV has no header row")
        output_header, converted, stats = convert_rows(
            list(reader),
            header,
            start_week=start_week,
            forecast_weeks=forecast_weeks,
        )

    with Path(output).open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=output_header)
        writer.writeheader()
        writer.writerows(converted)

    return stats


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Convert a theFPLkiwi projection CSV to fplreview-style fixture data."
    )
    parser.add_argument("source", type=Path, help="Path to the source theFPLkiwi CSV.")
    parser.add_argument("output", type=Path, help="Path to write the converted fixture CSV.")
    parser.add_argument("--start-week", type=positive_int, default=18)
    parser.add_argument("--forecast-weeks", type=positive_int, default=6)
    return parser.parse_args(argv)


def main(argv=None):
    options = parse_args(argv)
    stats = convert_file(
        options.source,
        options.output,
        start_week=options.start_week,
        forecast_weeks=options.forecast_weeks,
    )
    for key, value in stats.items():
        print("%s: %s" % (key, value))


if __name__ == "__main__":
    main()
