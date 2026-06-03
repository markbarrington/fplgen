---
date: 2026-06-03
topic: configurable-ga-runner
---

# Requirements: Configurable GA Runner

## Summary

Add command-line runtime controls to FPLgen's GA runner so normal runs remain compatible with today, while short deterministic optimizer runs become possible without editing source.

---

## Problem Frame

FPLgen now has a current input path through a single fplreview.com-style CSV and a synthetic golden fixture that validates import, known-squad scoring, and a tiny seeded GA path. The next blocker is day-to-day operability: routine run choices still live in source code. `code/GA.py` loads data and immediately starts a production-sized search with hard-coded population and generation settings, while `code/fpl.py` holds gameweek and forecast settings as module-level values.

That makes it awkward to run quick checks, compare seeded changes, or use a different projection export path. The goal of this first runner step is not to redesign FPLgen's state model, but to create a practical control surface that future work can build on.

---

## Key Decisions

- **Compatibility first:** Running `python3 code/GA.py` with no flags should preserve today's default behavior as closely as practical: load `data/fplreview.csv`, use the current gameweek and forecast horizon, create a large population, and allow up to the current generation limit.
- **CLI first:** The first control surface should be command-line flags. Config files, scenario files, presets, and richer run state can follow after the shape of the basic knobs is proven.
- **Determinism is a first-class use case:** The runner should support seeded short runs so future tests, debugging, and optimizer comparisons can distinguish behavior changes from random variation.
- **No scoring or optimizer rewrite:** This task should not change FPL scoring rules, transfer behavior, mutation/crossover strategy, or validity repair. It is about controlling an existing run.

---

## Requirements

**Runtime controls**

- R1. A no-flag run remains available through `python3 code/GA.py` and preserves the current default input path, population size, generation limit, gameweek, and forecast horizon.
- R2. The runner accepts an input CSV path so users can run against a fplreview.com export outside the default `data/fplreview.csv` location.
- R3. The runner accepts a population-size option for short smoke runs and longer search runs.
- R4. The runner accepts a generation-limit option so users can run bounded jobs without editing source.
- R5. The runner accepts a random-seed option that makes random team generation and GA evolution reproducible for the same input and settings.
- R6. The runner accepts gameweek and forecast-window options that affect which fplreview projection columns are required and loaded for the run.

**Run behavior**

- R7. The runner reports enough progress to show data import, population creation, generation progress, elapsed time, and the final fittest result.
- R8. The generation loop stops when either the max-fitness target is reached or the configured generation limit is reached.
- R9. Short deterministic runs should be practical for development, such as a tiny population and a few generations against the committed golden fixture.
- R10. Invalid or malformed runtime options fail before optimizer work begins with clear user-facing feedback.

**Compatibility and documentation**

- R11. Existing GA, scoring, import, transfer, and inspection-output behavior remain unchanged except where needed to respect the new runtime controls.
- R12. README guidance includes examples for the default run and a short seeded run.
- R13. Tests cover argument/control behavior and at least one tiny deterministic runner path without invoking a production-sized search.

---

## Key Flows

- F1. Default production-shaped run
  - **Trigger:** A user runs `python3 code/GA.py` with no flags.
  - **Steps:** FPLgen loads the default fplreview CSV, creates the default large population, runs up to the default generation limit, and outputs the final fittest result.
  - **Outcome:** Existing usage continues to work.
  - **Covered by:** R1, R7, R8, R11, R12

- F2. Short deterministic development run
  - **Trigger:** A developer passes a custom input path, small population, short generation limit, and seed.
  - **Steps:** FPLgen applies the provided controls, imports the selected projection CSV, runs a bounded seeded search, and outputs the final fittest result.
  - **Outcome:** The developer can reproduce the same run for debugging or comparison.
  - **Covered by:** R2, R3, R4, R5, R7, R8, R9, R13

- F3. Alternate projection horizon run
  - **Trigger:** A user passes gameweek and forecast-window options for a different fplreview export horizon.
  - **Steps:** FPLgen applies the selected horizon before import, validates that the required projection columns exist, and runs using those imported weekly scores.
  - **Outcome:** Users can run current-week scenarios without editing `code/fpl.py`.
  - **Covered by:** R6, R10, R11

---

## Acceptance Examples

- AE1. Given the default runtime data exists, when a user runs `python3 code/GA.py` with no flags, then FPLgen uses the same default population size, generation limit, gameweek, forecast horizon, and input path as the current script.
- AE2. Given a committed fplreview-style fixture, when a developer runs a tiny seeded job with a custom input path, small population, and short generation limit, then the runner completes without invoking the production-sized defaults.
- AE3. Given the same input CSV and seed, when the same short runner command is executed twice, then the random setup and resulting search path are reproducible enough for development comparison.
- AE4. Given the selected gameweek and forecast window require a missing fplreview projection column, when the runner starts, then it fails before optimizer work begins with a clear missing-column error.
- AE5. Given an invalid population size or generation limit, when the runner starts, then it fails before import or evolution begins.

---

## Scope Boundaries

- Config files, scenario files, named presets, and CLI-over-config overrides are deferred.
- A typed `RunConfig` object and broader `FplContext` state model are deferred.
- Historical real-data fixtures from theFPLkiwi or fplcache are deferred.
- Validity repair, mutation/crossover tuning, and scoring or transfer rule changes are out of scope for this task.
- Packaging a console script such as `fplgen` is optional future workflow polish; this task can continue to use `python3 code/GA.py`.

---

## Dependencies / Assumptions

- The existing fplreview importer can continue to be the runtime data source.
- Gameweek and forecast controls will initially work with the current module-level settings rather than requiring a full state-management redesign.
- The committed golden fixture remains the best development fixture for tiny deterministic runner validation.

---

## Sources / Research

- `docs/ideation/2026-06-02-repo-improvements-ideation.md`
- `docs/ideation/2026-06-02-hardcoded-elements-config-ideation.md`
- `docs/plans/2026-06-02-001-feat-fplreview-import-plan.md`
- `docs/plans/2026-06-02-002-feat-golden-fplreview-fixture-plan.md`
- `code/GA.py`
- `code/fpl.py`
- `tests/test_fplreview_golden.py`
