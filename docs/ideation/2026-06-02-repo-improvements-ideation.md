---
date: 2026-06-02
topic: repo-improvements
focus: potential improvements for FPLgen
mode: repo-grounded
---

# Ideation: Repo Improvements for FPLgen

## Grounding Context

FPLgen is a small Python project for generating Fantasy Premier League squads with a genetic algorithm. The core behavior is concentrated in `code/fpl.py`, with GA orchestration in `code/GA.py`, `code/Algorithm.py`, `code/Population.py`, and `code/Individual.py`.

The README documents three runtime inputs under `data/`: `playerdata`, `fixturedata`, and `playerlast10.csv`. These files are intentionally not committed. The repo is old enough that the Fantasy Premier League APIs and surrounding data ecosystem have changed since the original implementation, so preserving the old scraper-shaped data contract is less useful than moving to a current import path.

The preferred data direction is to import from a single file exported from fplreview.com. There is a GitHub issue posted for this change, although this pass could not verify the issue number because GitHub API access was unavailable in the sandbox. Current tests cover path resolution and a few `validteam()` cases, but they do not exercise file import, projections, scoring, transfers, or GA evolution.

Notable constraints and pain points:

- `fpl.py` holds global mutable state for players, fixtures, budget, gameweek, forecast weeks, chips, and transfer behavior.
- `getplayerdata()` expects older scraper-shaped inputs and writes `data/playerkeydata` as a side effect.
- `lookaheadpoints()` indexes fixtures with `fixtures[player["id"] - 1]`, so player IDs and fixture rows must stay aligned.
- The most useful data contract improvement is likely a new single-file fplreview.com importer rather than a compatibility layer around the old three-file scraper input.
- `GA.py` runs work at import time, creates a population of 10,000, and loops up to 300 generations with no CLI controls.
- `Population.get_average_fitness()` reads cached scores directly, which can include `-1` for unevaluated individuals unless fitness was computed first.
- The repo already has a recent ideation note for a synthetic test data set; that note is treated as background context here.

External context: current FPL tooling commonly documents `bootstrap-static` for player data and `element-summary/{player_id}` for per-player fixtures/history, while this repo expects a three-file scraper-shaped contract. fplreview.com-style projections are also used by adjacent FPL optimization tools as loadable projection data. Useful references include the `fpl` package docs, FPLstat's data reference, Oliver Looney's FPL API explainer, and FPL Optimized's load-data page:

- https://fpl.readthedocs.io/en/latest/_modules/fpl/fpl.html
- https://james-leslie.github.io/fplstat/data-reference/
- https://www.oliverlooney.com/blogs/FPL-APIs-Explained
- https://fploptimized.com/load.html

## Topic Axes

- Data contract and fixtures
- Scoring correctness
- GA runtime and reproducibility
- State and architecture
- Developer workflow and packaging

## Ranked Ideas

### 1. Import a Single fplreview.com Export File

**Description:** Replace the old three-file runtime import path with a single-file importer for fplreview.com exports. The importer should normalize the exported player projections into the internal shape needed for squad generation, scoring, transfer planning, and inspection output. Use the posted GitHub issue as the implementation brief once its exact fields and acceptance criteria are available.

**Axis:** Data contract and fixtures

**Basis:** `direct:` The repo currently expects old scraper-shaped inputs, and the user clarified that the FPL APIs have changed since the project was written and that a GitHub issue now asks for import from a single fplreview.com export file.

**Rationale:** This is now the highest-leverage move because it updates the project around the data source Mark actually wants to use. It reduces dependency on stale API/scraper assumptions and gives the rest of the optimizer a cleaner, current input contract.

**Downsides:** Requires a representative fplreview.com export sample and a decision on which columns become the internal projection fields.

**Confidence:** 95%

**Complexity:** Medium

**Status:** Explored

### 2. Build a Golden fplreview.com Import Fixture

**Description:** Add a small representative fplreview.com export under `tests/fixtures/` and use it to test import, normalization, projection fields, unavailable or low-minutes players, and a known legal squad. Keep any synthetic data in the same column shape as the real export rather than recreating the old `playerdata`/`fixturedata`/`playerlast10.csv` trio.

**Axis:** Data contract and fixtures

**Basis:** `direct:` Existing tests do not exercise runtime data import, and the desired future import surface is a single fplreview.com export file.

**Rationale:** A golden fixture lets the project change data import without guessing. It should also become the safety net for scoring and GA smoke tests.

**Downsides:** Needs either a committed sanitized sample or a generator that faithfully mimics the export columns.

**Confidence:** 93%

**Complexity:** Medium

**Status:** Unexplored

### 3. Add a Reproducible, Configurable GA Runner

**Description:** Replace the hard-coded script behavior in `GA.py` with a small CLI entrypoint that accepts the fplreview.com export path, population size, generation limit, random seed, gameweek, and forecast weeks. Keep current defaults available only where they still make sense, but make short deterministic runs possible for tests and debugging.

**Axis:** GA runtime and reproducibility

**Basis:** `direct:` `GA.py` immediately imports player data, creates `Population(10000, True)`, and loops until generation 300 or an unreachable-looking max fitness target.

**Rationale:** A configurable runner makes the project usable with a real fplreview.com export and with tiny fixtures. It also lets future work compare optimizer changes with the same seed instead of guessing whether a score changed because of randomness.

**Downsides:** Needs modest restructuring to avoid breaking `python3 code/GA.py`.

**Confidence:** 90%

**Complexity:** Medium

**Status:** Unexplored

### 4. Split Import, Projection, and Scoring Into Explicit Boundaries

**Description:** Separate the new fplreview.com file import, projection normalization, scoring inputs, and inspection output into distinct functions or objects. This can be a stepping stone toward an `FplContext` that owns players, budget, gameweek, chip flags, and scoring constants.

**Axis:** State and architecture

**Basis:** `direct:` `getplayerdata()` currently mixes file IO, field enrichment, projection calculations, global assignment, and writing `playerkeydata`, while `fpl.py` defines many module globals for run state.

**Rationale:** The fplreview.com import change is a natural moment to stop mixing data acquisition with scoring behavior. A boundary-first refactor reduces hidden coupling without requiring a full rewrite.

**Downsides:** Needs discipline to keep the first pass narrow; a full context rewrite is tempting but should be staged.

**Confidence:** 86%

**Complexity:** Medium

**Status:** Unexplored

### 5. Lock Down Scoring and Transfer Edge Cases

**Description:** Add focused tests for scoring formation selection, captain/triple-captain behavior, bench boost, unavailable players or low projected minutes, blank or missing projection weeks, budget-constrained transfers, and invalid teams returning zero. Use builders plus the fplreview.com golden fixture rather than live API data.

**Axis:** Scoring correctness

**Basis:** `direct:` `scoreteam()` mutates transfer patterns and bank state, `score()` chooses a starting lineup from sorted weekly projections, and the future importer will need to map fplreview.com projection columns into the week scores that scoring expects.

**Rationale:** The scoring logic is where domain value lives, but today it is mostly unprotected. These tests would let the project improve optimizer mechanics without accidentally changing FPL rules.

**Downsides:** Requires deciding whether current behavior is intended in places where code comments and live behavior diverge.

**Confidence:** 87%

**Complexity:** Medium

**Status:** Unexplored

### 6. Add Validity Repair Instead of Letting Broken Individuals Score Zero

**Description:** Implement or replace `repairteam()` so crossover and mutation produce valid squads more often, or make mutation position-aware enough to preserve squad shape, budget, club limits, and uniqueness. Track invalid-rate during evolution as a metric.

**Axis:** GA runtime and reproducibility

**Basis:** `direct:` `Algorithm.evolve_population()` has repair logic commented out, `repairteam()` currently returns the team unchanged, and `scoreteam()` returns zero for invalid teams.

**Rationale:** If many evolved individuals are invalid, the GA spends search budget rediscovering legality instead of improving team quality. A repair or constraint-preserving mutation step could improve convergence without changing the scoring model.

**Downsides:** Needs measurement first; a naive repair function could bias the search or hide invalid-generation bugs.

**Confidence:** 78%

**Complexity:** Medium

**Status:** Unexplored

### 7. Modernize the Developer Workflow Around Import-and-Run

**Description:** Add a proper console script, test command, lint/format baseline, and README examples for running against a fplreview.com export. Keep the implementation plain Python, but make `fplgen --input path/to/export.csv --seed 1 --generations 20` style workflows obvious.

**Axis:** Developer workflow and packaging

**Basis:** `direct:` `pyproject.toml` exists with project metadata and pytest pythonpath, but the README still points to `python3 code/GA.py` and there is no packaged entrypoint.

**Rationale:** This is a low-risk way to make the repo easier to run, test, and extend around the new data source. It also creates a natural home for configuration once the GA runner becomes parameterized.

**Downsides:** Lower algorithmic value than test/scoring work; should not distract from data contract improvements.

**Confidence:** 84%

**Complexity:** Low

**Status:** Unexplored

## Rejection Summary

| # | Idea | Reason Rejected |
|---|------|-----------------|
| 1 | Replace the GA with an integer-programming optimizer | Interesting external direction, but too close to replacing the subject rather than improving this GA repo. |
| 2 | Update the repo to call current FPL APIs directly | Less useful than the stated target: import from a single fplreview.com export file. |
| 3 | Add a web dashboard | Too expensive relative to current repo maturity; the run/data/scoring surface needs stabilization first. |
| 4 | Convert everything to pandas | Could help analysis, but no direct basis that tabular processing is the current bottleneck. |
| 5 | Preserve the old three-file scraper contract as the primary path | The repo's age and changed FPL APIs make this lower value than moving to fplreview.com import. |
| 6 | Tune mutation/crossover constants immediately | Premature without reproducible seeds, invalid-rate metrics, and scoring regression tests. |
| 7 | Delete legacy comments and constants as cleanup | Below the meeting-test floor as a standalone repo improvement, though it can accompany deeper refactors. |
| 8 | Switch from unittest to pytest wholesale | Not enough value by itself; the current test framework works for the next set of regression tests. |
| 9 | Add type hints everywhere | Useful eventually, but too broad; stronger if scoped to the data adapter/context work. |

## Recommendation

Start with Ideas 1, 2, 3, and 5 as the first improvement wave:

1. Define and implement the single-file fplreview.com export importer.
2. Add a golden fplreview.com import fixture.
3. Add deterministic short-run controls to the GA entrypoint.
4. Cover the scoring and transfer rules that matter most.

Those moves create enough safety to tackle the larger architectural improvements: boundary-first refactor, context object, and validity repair.
