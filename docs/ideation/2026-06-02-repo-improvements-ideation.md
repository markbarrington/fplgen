---
date: 2026-06-02
topic: repo-improvements
focus: potential improvements for FPLgen
mode: repo-grounded
---

# Ideation: Repo Improvements for FPLgen

## Grounding Context

FPLgen is a small Python project for generating Fantasy Premier League squads with a genetic algorithm. The core behavior is concentrated in `code/fpl.py`, with GA orchestration in `code/GA.py`, `code/Algorithm.py`, `code/Population.py`, and `code/Individual.py`.

The README now documents the preferred runtime input: a single projection CSV at `data/fplreview.csv`. The older runtime path used three files under `data/`: `playerdata`, `fixturedata`, and `playerlast10.csv`. Runtime data is intentionally not committed. The repo is old enough that the Fantasy Premier League APIs and surrounding data ecosystem have changed since the original implementation, so preserving the old scraper-shaped data contract is less useful than moving to a current import path.

The preferred data direction is to import from a single file exported from fplreview.com. Current tests cover path resolution, a few `validteam()` cases, fplreview CSV import mapping, a synthetic golden fplreview fixture, known legal squad scoring, and a tiny seeded GA smoke path. They do not yet exercise enough transfer, chip, scoring edge-case, or real-export behavior.

Notable constraints and pain points:

- `fpl.py` holds global mutable state for players, fixtures, budget, gameweek, forecast weeks, chips, and transfer behavior.
- `getplayerdata()` loads `fplreview.csv`, maps projection rows to FPLgen player dictionaries, assigns global player state, and writes `data/playerkeydata` as a side effect.
- `map_fplreview_rows()` requires `Pos`, `ID`, `Name`, `BV`, `SV`, `Team`, and configured gameweek point columns.
- The older `lookaheadpoints()` path still indexes fixtures with `fixtures[player["id"] - 1]`, so player IDs and fixture rows must stay aligned if that path remains under test.
- `GA.py` runs work at import time, creates a population of 10,000, and loops up to 300 generations with no CLI controls.
- `Population.get_average_fitness()` reads cached scores directly, which can include `-1` for unevaluated individuals unless fitness was computed first.

External context: current FPL tooling commonly documents `bootstrap-static` for player data and `element-summary/{player_id}` for per-player fixtures/history. fplreview.com-style projections are also used by adjacent FPL optimization tools as loadable projection data. Two public historical sources look especially useful for test data:

- `Randdalf/fplcache`: historical compressed `bootstrap-static` snapshots. Best for realistic FPL player, team, status, cost, and event shape.
- `theFPLkiwi/theFPLkiwi`: historical projection resources. Its README says `Old_Seasons` contains previous seasons' weekly projections and hindsight-optimisation data, while current-season projection folders contain weekly projections. It also warns that some projected players may have ID `0` or omit players no longer considered relevant, so importer tests should handle filtering and zero-fill behavior.

Useful references include the `fpl` package docs, FPLstat's data reference, Oliver Looney's FPL API explainer, FPL Optimized's load-data page, Randdalf's fplcache, and theFPLkiwi:

- https://fpl.readthedocs.io/en/latest/_modules/fpl/fpl.html
- https://james-leslie.github.io/fplstat/data-reference/
- https://www.oliverlooney.com/blogs/FPL-APIs-Explained
- https://fploptimized.com/load.html
- https://github.com/Randdalf/fplcache
- https://github.com/theFPLkiwi/theFPLkiwi

## Topic Axes

- Data contract and fixtures
- Scoring and transfer correctness
- GA runtime and reproducibility
- Scenario state and architecture
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

**Status:** Shipped

### 2. Build a Golden fplreview.com Import Fixture

**Description:** Add a small representative fplreview.com export under `tests/fixtures/` and use it to test import, normalization, projection fields, low-projection players, a known legal squad, and a tiny seeded GA smoke path. Keep synthetic data in the same column shape as the real export rather than recreating the old `playerdata`/`fixturedata`/`playerlast10.csv` trio.

**Axis:** Data contract and fixtures

**Basis:** `direct:` Existing tests do not exercise runtime data import, and the desired future import surface is a single fplreview.com export file.

**Rationale:** A golden fixture lets the project change data import without guessing. It should also become the safety net for scoring and GA smoke tests.

**Downsides:** The shipped fixture is synthetic and intentionally compact, so it proves wiring and characterization behavior rather than real projection quality or full optimizer robustness.

**Confidence:** 93%

**Complexity:** Medium

**Status:** Shipped

### 3. Add a Reproducible, Configurable GA Runner

**Description:** Replace the hard-coded script behavior in `GA.py` with a small CLI entrypoint that accepts the fplreview.com export path, population size, generation limit, random seed, gameweek, and forecast weeks. Keep current defaults available only where they still make sense, but make short deterministic runs possible for tests and debugging.

**Axis:** GA runtime and reproducibility

**Basis:** `direct:` `GA.py` immediately imports player data, creates `Population(10000, True)`, and loops until generation 300 or an unreachable-looking max fitness target.

**Rationale:** A configurable runner makes the project usable with a real fplreview.com export and with tiny fixtures. It also lets future work compare optimizer changes with the same seed instead of guessing whether a score changed because of randomness.

**Downsides:** Needs modest restructuring to avoid breaking `python3 code/GA.py`.

**Confidence:** 90%

**Complexity:** Medium

**Status:** Shipped

### 4. Add Historical Projection Fixtures From theFPLkiwi

**Description:** Pin one historical theFPLkiwi projection CSV and convert it into the same shape as a fplreview export. Keep only rows with nonzero source IDs, map name, position, team, price, and weekly projection columns to `Pos`, `ID`, `Name`, `BV`, `SV`, `Team`, and `*_Pts`. Pairing with fplcache to zero-fill selectable FPL IDs missing from the projection source remains follow-up work.

**Axis:** Data contract and fixtures

**Basis:** `external:` theFPLkiwi's repository documents historical weekly projections under `Old_Seasons`; this repo now optimizes against projected point columns.

**Rationale:** This is the best real-world source for optimizer input because it contains actual projected points across gameweeks rather than just live FPL state. It complements the synthetic golden fixture by exposing real naming, ID, team, price, and projection quirks.

**Downsides:** Column naming may vary by season, and historical projections are a third-party model output rather than official FPL data.

**Confidence:** 88%

**Complexity:** Medium

**Status:** Shipped. The repo now includes a converted 2023/24 theFPLkiwi historical projection-row fixture, provenance docs, a regeneration utility, import/coverage tests, and a valid-squad scoring check. fplcache zero-fill pairing remains deferred.

### 5. Add Scenario-Based Existing Squad Optimization

**Description:** Add a scenario-file input for gameweeks where the manager already has a squad. If the configured gameweek is 1, FPLgen can generate a fresh squad and no current squad is required. If the configured gameweek is not 1, the scenario must supply the current squad by FPL ID, current bank, saved free transfers, and chip availability. Wildcard and Free Hit should not be scenario modes; they should be optimizer options that the run may examine and time when allowed.

**Axis:** Scenario state and architecture

**Basis:** `direct:` `Individual.__init__()` always calls `fpl.generateteam()`, `currentteam` exists but is unused in `generateteam()`, `scoreteam()` skips transfers in week 1 because it assumes a newly generated starting team, and `scoreteam()` derives bank as `budget - teamvalue(team)` instead of using an existing manager's actual bank.

**Rationale:** This is the missing core workflow for week-to-week FPL use. Fresh squad generation is only valid for gameweek 1; after that, every realistic run starts from an owned squad, a live bank, and saved free transfers. Wildcard and Free Hit are then choices the optimizer may make within that starting scenario, not separate ways of describing the starting state. Making that state explicit also gives the project a natural first scenario-file contract before a broader `RunConfig` or `FplContext` refactor.

**Downsides:** This touches core transfer semantics, not just input parsing. It needs careful regression fixtures for GW1 fresh-squad behavior, required current-squad input after GW1, first-week transfers, bank preservation, saved free transfer caps, wildcard timing, and Free Hit restoration.

**Confidence:** 94%

**Complexity:** Medium-High

**Status:** Proposed next

### 6. Add Historical FPL State Fixtures From fplcache

**Description:** Pin one `Randdalf/fplcache` `bootstrap-static` snapshot and trim it to a compact player/team fixture. Use `elements` for IDs, names, element type, team IDs, status, price, minutes, and total points; use `teams` to verify team-name mapping; and use `events` only where it helps confirm gameweek context.

**Axis:** Data contract and fixtures

**Basis:** `external:` fplcache is a historical cache of FPL `bootstrap-static` snapshots, which is the official-shaped state data adjacent to projection input.

**Rationale:** This is strongest as schema-drift protection and realistic player-pool data, paired with theFPLkiwi or synthetic projections for expected points.

**Downsides:** `bootstrap-static` is not a projection source, so it does not directly feed FPLgen's current optimizer without separate projected points.

**Confidence:** 84%

**Complexity:** Medium

**Status:** Unexplored

### 7. Split Import, Projection, and Scoring Into Explicit Boundaries

**Description:** Separate the new fplreview.com file import, projection normalization, scoring inputs, and inspection output into distinct functions or objects. This can be a stepping stone toward an `FplContext` that owns players, budget, gameweek, chip flags, and scoring constants.

**Axis:** Scenario state and architecture

**Basis:** `direct:` `getplayerdata()` currently mixes file IO, field enrichment, projection calculations, global assignment, and writing `playerkeydata`, while `fpl.py` defines many module globals for run state.

**Rationale:** The fplreview.com import change is a natural moment to stop mixing data acquisition with scoring behavior. A boundary-first refactor reduces hidden coupling without requiring a full rewrite.

**Downsides:** Needs discipline to keep the first pass narrow; a full context rewrite is tempting but should be staged.

**Confidence:** 86%

**Complexity:** Medium

**Status:** Unexplored

### 8. Lock Down Scoring and Transfer Edge Cases

**Description:** Add focused tests for scoring formation selection, captain/triple-captain behavior, bench boost, unavailable players or low projected minutes, blank or missing projection weeks, budget-constrained transfers, and invalid teams returning zero. Use builders plus the fplreview.com golden fixture rather than live API data.

**Axis:** Scoring and transfer correctness

**Basis:** `direct:` `scoreteam()` mutates transfer patterns and bank state, `score()` chooses a starting lineup from sorted weekly projections, and the future importer will need to map fplreview.com projection columns into the week scores that scoring expects.

**Rationale:** The scoring logic is where domain value lives, but today it is mostly unprotected. These tests would let the project improve optimizer mechanics without accidentally changing FPL rules.

**Downsides:** Requires deciding whether current behavior is intended in places where code comments and live behavior diverge.

**Confidence:** 87%

**Complexity:** Medium

**Status:** Unexplored

### 9. Add Validity Repair Instead of Letting Broken Individuals Score Zero

**Description:** Implement or replace `repairteam()` so crossover and mutation produce valid squads more often, or make mutation position-aware enough to preserve squad shape, budget, club limits, and uniqueness. Track invalid-rate during evolution as a metric.

**Axis:** GA runtime and reproducibility

**Basis:** `direct:` `Algorithm.evolve_population()` has repair logic commented out, `repairteam()` currently returns the team unchanged, and `scoreteam()` returns zero for invalid teams.

**Rationale:** If many evolved individuals are invalid, the GA spends search budget rediscovering legality instead of improving team quality. A repair or constraint-preserving mutation step could improve convergence without changing the scoring model.

**Downsides:** Needs measurement first; a naive repair function could bias the search or hide invalid-generation bugs.

**Confidence:** 78%

**Complexity:** Medium

**Status:** Unexplored

### 10. Modernize the Developer Workflow Around Import-and-Run

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

Ideas 1, 2, 3, and 4 have shipped: FPLgen now imports a single fplreview.com CSV, has a synthetic golden fixture that proves import, known-squad scoring, and a tiny seeded GA path, exposes a configurable GA runner for short deterministic runs, and includes a historical theFPLkiwi projection fixture for realistic projection-row tests.

The next improvement wave should start with Idea 5, because it unlocks the normal in-season workflow the tool is currently missing. The priority order should be:

1. Add scenario-based existing squad optimization: generate a fresh squad only for gameweek 1, and require a current squad for every later gameweek.
2. Treat wildcard and Free Hit as optimizer chip options inside the scenario, including the ability to decide the best week to play each allowed chip.
3. Add focused transfer and scenario regression fixtures as part of that work, especially required current-squad input after gameweek 1, first-week transfers, bank preservation, saved free transfers up to 5, wildcard timing, and Free Hit squad restoration.
4. Add a pinned fplcache `bootstrap-static` fixture for realistic player/team mapping once the scenario contract needs richer official-state coverage.
5. Broaden scoring and transfer edge-case coverage beyond the scenario feature.
6. Add deterministic optimizer health metrics after the realistic fixture base is broader.

Those moves create enough safety to tackle the larger architectural improvements: boundary-first refactor, context object, and validity repair. The scenario feature should be treated as the first concrete step toward `RunConfig` and `FplContext`, not as a separate one-off input path.
