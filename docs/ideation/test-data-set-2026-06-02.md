# Test Data Set Ideation: FPLgen

Date: 2026-06-02

## Topic

How to create a test data set for this repository.

## Grounding

FPLgen expects runtime data in three files under `data/`: `playerdata`, `fixturedata`, and `playerlast10.csv`. Those files are intentionally not committed. The current committed test coverage uses in-memory player dictionaries and only checks path handling plus `validteam` basics.

Important code constraints:

- `getplayerdata()` loads `playerdata` as JSON, `playerlast10.csv` as CSV, and `fixturedata` as newline-delimited JSON.
- `fixturedata` is accessed by `fixtures[player["id"] - 1]`, so fixture records must align with contiguous player IDs unless the loader changes.
- `lookaheadpoints()` needs each fixture record to include `history_past` and `fixtures`.
- `validteam()` enforces 15-player squad shape, max 3 per club, unique player IDs, budget, and a stricter no-duplicate-club-per-position rule.
- `generateteam()` uses global `players` and random selection, so a test corpus needs enough available players by position and club to avoid retry loops.

External context checked: Fantasy Premier League data ecosystems commonly derive from FPL API-style player, fixture, and per-player detail data; the related project in this repo is `markbarrington/fplscraper`, but the local loader defines the exact contract this test data must satisfy.

## Ranked Ideas

### 1. Generated Minimal Golden Corpus

Create a script or fixture helper that generates a compact, deterministic dataset into `tests/fixtures/minimal/`:

- `playerdata`: 24 to 32 synthetic players with contiguous IDs, stable codes, costs, positions, teams, statuses, minutes, total points, and fixture history fields.
- `fixturedata`: one newline-delimited JSON record per player ID with `history_past` and six future `fixtures`.
- `playerlast10.csv`: rows keyed by player code, including home and away scoring aggregates.

This is the strongest option because it matches the real loader surface while keeping the data small, readable, and reproducible. It can support tests for `getplayerdata()`, `lookaheadpoints()`, `scoreteam()`, and a small deterministic `Population` run.

Tradeoff: the generator must encode the old data shape carefully, but that is also valuable documentation.

### 2. Two-Tier Fixtures: Unit Builders Plus Integration Corpus

Keep the lightweight in-memory builders already used by smoke tests, but add a file-backed corpus for loader and scoring tests.

Use:

- `tests/helpers.py` for player/team builders.
- `tests/fixtures/minimal/` for realistic file inputs.
- Tests that copy or point loader resolution at the fixture directory without polluting `data/`.

This gives the best day-to-day ergonomics. Unit tests stay fast and obvious; integration tests prove the data-file contract still works.

Tradeoff: needs a small amount of test harness work because `data_file()` currently searches fixed locations.

### 3. Contract Snapshot From `fplscraper`

Capture one tiny representative output from the related scraper project and trim it to a stable subset.

This would reveal mismatches between FPLgen and scraper output better than fully synthetic data, especially around field names and row ordering.

Tradeoff: real-world snapshots can become noisy, may carry licensing or freshness questions, and can obscure intent if every field is preserved.

### 4. Scenario Matrix Corpus

Create several named mini-datasets, each targeting one behavior:

- `happy_path`: enough available players for a valid squad and six scored gameweeks.
- `unavailable_players`: verifies unavailable players are zeroed.
- `blank_fixture`: verifies a player with no fixture does not crash scoring.
- `double_gameweek`: verifies multiple fixtures in one event add points.
- `budget_pressure`: verifies generation/scoring around tight costs.
- `non_contiguous_ids`: intentionally fails or documents the current fixture indexing limitation.

This is excellent for regression testing once the first corpus exists.

Tradeoff: more files and more maintenance. Better as a second wave than the first move.

### 5. Property-Style Synthetic Dataset Factory

Build a configurable factory that can generate many legal FPL-like player pools with seeded randomness, then assert invariants such as "generated teams are always 15 players" or "scoreteam never raises for legal fixture sets."

This could expose edge cases in the random GA flow.

Tradeoff: too much machinery for the repo's current test depth. It should follow a fixed golden corpus, not precede it.

## Rejected Ideas

### Commit Full Real Runtime Data

Rejected because the README says runtime data is intentionally kept out of Git, and large/live FPL data would make tests brittle.

### Use Only In-Memory Dictionaries

Rejected as the primary strategy because it would not exercise the file contract, CSV parsing, fixture ordering, or `playerkeydata` output.

### Mock `getplayerdata()` Heavily

Rejected because the loader is exactly where the risk is. Mocking it would bypass the most fragile integration point.

### Download Live FPL Data During Tests

Rejected because tests should be deterministic, offline, and independent of current season API shape.

## Recommendation

Start with Idea 1 plus the useful parts of Idea 2:

1. Add `tests/fixtures/minimal/` with a generated golden corpus.
2. Add a fixture helper that temporarily points data loading at that directory or copies files into a temporary data directory.
3. Add tests for:
   - `getplayerdata()` loads all three inputs and writes `playerkeydata`.
   - every loaded player receives `lookaheadpoints`, `thisweekpoints`, `ppg`, and week keys `1` through `6`.
   - unavailable players get zero projected week scores.
   - a known legal squad scores above zero.
   - a tiny seeded population can be created without hanging or returning malformed individuals.

The first corpus should be synthetic, not live data. Use club and player names that make intent obvious, keep player IDs contiguous, and preserve the old FPL/scraper-shaped fields that the code currently expects.

## Suggested Dataset Shape

Minimum practical corpus:

- 28 players:
  - 4 goalkeepers
  - 8 defenders
  - 10 midfielders
  - 6 forwards
- 10 to 12 clubs represented, with no more than 3 players per club in any intended legal squad.
- Costs mostly 45 to 75, with one expensive scenario set.
- At least one unavailable player per position.
- Six future fixtures per player covering gameweeks 3 through 8, matching the current `gameweek = 3` and `forecastweeks = 6`.
- `history_past` includes a `2015/16` row, even if current gameweek scoring dominates at the moment.

## Next Step

Run `ce-brainstorm` on the selected direction, likely "Generated Minimal Golden Corpus", to define the exact fixture schema, test harness changes, and naming before implementation.
