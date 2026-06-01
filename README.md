# FPLgen

Genetic algorithm for building English Premier League Fantasy Football teams.

The project imports Fantasy Premier League player and fixture data, estimates player scores across upcoming gameweeks, and searches for a high-scoring valid squad.

## Quick start

```sh
python3 code/GA.py
```

## Data files

Runtime data is intentionally kept out of Git. Put these files in `data/`:

- `playerdata`: JSON player data in the format produced by `fplscraper`
- `fixturedata`: one JSON fixture record per line
- `playerlast10.csv`: recent player home/away scoring data

The loader also checks the current working directory and `code/` for backwards compatibility with the original layout.

The run writes `data/playerkeydata`, a generated inspection file with player scoring inputs and projections.

## Development

Run the syntax and smoke checks with:

```sh
python3 -m py_compile code/*.py
python3 -m unittest discover -s tests
```

## Related project

Input data can be produced by:

https://github.com/markbarrington/fplscraper

## Credits

The genetic algorithm was based on Arthur Rebelo's Python port of Lee Jacobson's beginner genetic algorithm tutorial.
