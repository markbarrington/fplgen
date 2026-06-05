# FPLgen

Genetic algorithm for building English Premier League Fantasy Football teams.

The project imports fplreview.com player projection exports and searches for a high-scoring valid squad.

## Quick start

For a GW1 fresh-squad search, run with a GW1 projection export:

```sh
python3 code/GA.py --gameweek 1
```

For a normal non-GW1 planning run, provide the current squad situation as a scenario file:

```sh
python3 code/GA.py --input data/fplreview.csv --gameweek 3 --scenario data/my-scenario.json
```

For a short deterministic development run, pass explicit controls and a test/demo scenario:

```sh
python3 code/GA.py --input tests/fixtures/fplreview_golden.csv --gameweek 3 --scenario examples/scenario_template.json --population 6 --generations 2 --seed 7
```

Useful runtime options include:

- `--input`: fplreview CSV export path
- `--scenario`: JSON file with current squad, bank, saved free transfers, and matching gameweek
- `--population`: GA population size
- `--generations`: maximum generation count
- `--seed`: random seed for reproducible runs
- `--gameweek`: first gameweek projection column to load
- `--forecastweeks`: number of gameweeks to load

GW1 can run without a scenario because FPLgen is choosing a fresh starting squad. Runs after GW1 require a scenario file so the optimizer starts from the actual owned squad instead of inventing a new one. The scenario `gameweek` must match `--gameweek`; the CLI remains the runtime control, and the scenario field catches stale files.

## Scenario files

Scenario files describe FPL situation only:

```json
{
  "gameweek": 3,
  "bank": 0.7,
  "saved_free_transfers": 2,
  "current_squad": [201, 202, 204, 205, 206, 207, 208, 211, 212, 213, 214, 215, 218, 219, 220]
}
```

Use `examples/scenario_template.json` as an editable starting point. Replace the player IDs with the 15 FPL IDs for the real current squad, set `bank` as the displayed decimal amount, and set `saved_free_transfers` to the available free transfers.

To generate a valid test/demo scenario from a projection CSV:

```sh
python3 code/generate_scenario.py --input tests/fixtures/fplreview_golden.csv --output /tmp/scenario.json --gameweek 3 --bank 0.7 --saved-free-transfers 2 --seed 7
```

Generated scenarios are useful for tests and demos. They are not live FPL team sync and should not be treated as recommended manager squads.

## Data files

Runtime data is intentionally kept out of Git. Export projections from fplreview.com and save the CSV as:

```text
data/fplreview.csv
```

FPLgen imports and normalizes the configured gameweek columns from the export as the expected score for each player. Those values are loaded directly into the optimizer's scoring input; FPLgen does not apply additional projection adjustments for strength of schedule, home/away splits, availability, or expected minutes.

The run writes `data/playerkeydata`, a generated inspection file showing the normalized projection values used by the optimizer.

## Development

Run the syntax and smoke checks with:

```sh
python3 -m py_compile code/*.py
python3 -m unittest discover -s tests
```

The test suite includes two committed projection fixtures:

- `tests/fixtures/fplreview_golden.csv`: synthetic validation data that checks
  import, known legal squad scoring, existing-squad scenarios, and a tiny
  seeded GA smoke path.
- `tests/fixtures/fplkiwi_historical.csv`: a historical theFPLkiwi
  projection-row corpus converted to fplreview-style columns for realistic
  import, squad-scoring, and bounded runner-path coverage.

The historical fixture is realistic projection input, not official FPL state
and not a complete selectable-player universe. It does not define optimizer
score or timing benchmarks.

## Credits

The genetic algorithm was based on Arthur Rebelo's Python port of Lee Jacobson's beginner genetic algorithm tutorial.
