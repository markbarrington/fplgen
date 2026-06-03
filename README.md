# FPLgen

Genetic algorithm for building English Premier League Fantasy Football teams.

The project imports fplreview.com player projection exports and searches for a high-scoring valid squad.

## Quick start

```sh
python3 code/GA.py
```

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

The test suite includes a synthetic golden fplreview fixture that checks the
repo still works end to end: import, known legal squad scoring, and a tiny
seeded GA smoke path. The fixture is validation data, not a real projection
quality sample; real-export validation can be added separately later.

## Credits

The genetic algorithm was based on Arthur Rebelo's Python port of Lee Jacobson's beginner genetic algorithm tutorial.
