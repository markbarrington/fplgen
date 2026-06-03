# FPLgen

Genetic algorithm for building English Premier League Fantasy Football teams.

The project imports fplreview.com player projection exports and searches for a high-scoring valid squad.

## Quick start

```sh
python3 code/GA.py
```

The default run preserves the original production-sized search settings. For a
short deterministic development run, pass explicit controls:

```sh
python3 code/GA.py --input tests/fixtures/fplreview_golden.csv --population 6 --generations 2 --seed 7
```

Useful runtime options include:

- `--input`: fplreview CSV export path
- `--population`: GA population size
- `--generations`: maximum generation count
- `--seed`: random seed for reproducible runs
- `--gameweek`: first gameweek projection column to load
- `--forecastweeks`: number of gameweeks to load

## Data files

Runtime data is intentionally kept out of Git. Export projections from fplreview.com and save the CSV as:

```text
data/fplreview.csv
```

FPLgen uses the configured gameweek columns from the export as the expected score for each player. Those values are loaded directly; FPLgen does not apply additional projection adjustments for strength of schedule, home/away splits, availability, or expected minutes.

The run writes `data/playerkeydata`, a generated inspection file showing the imported scoring values used by the optimizer.

## Development

Run the syntax and smoke checks with:

```sh
python3 -m py_compile code/*.py
python3 -m unittest discover -s tests
```

The test suite includes two committed projection fixtures:

- `tests/fixtures/fplreview_golden.csv`: synthetic validation data that checks
  import, known legal squad scoring, and a tiny seeded GA smoke path.
- `tests/fixtures/fplkiwi_historical.csv`: a historical theFPLkiwi
  projection-row corpus converted to fplreview-style columns for realistic
  import, squad-scoring, and bounded runner-path coverage.

The historical fixture is realistic projection input, not official FPL state
and not a complete selectable-player universe. It does not define optimizer
score or timing benchmarks.

## Credits

The genetic algorithm was based on Arthur Rebelo's Python port of Lee Jacobson's beginner genetic algorithm tutorial.
