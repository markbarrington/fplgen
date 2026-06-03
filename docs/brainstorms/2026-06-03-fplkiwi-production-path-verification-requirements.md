---
date: 2026-06-03
topic: fplkiwi-production-path-verification
---

# FPLkiwi Production Path Verification Requirements

## Summary

Add a lightweight verification check that runs FPLgen's production GA runner path against the committed historical theFPLkiwi fixture. The check should prove that realistic projection input can complete a bounded run and return a nonzero result without turning the fixture into an optimizer benchmark.

---

## Problem Frame

FPLgen now has two useful confidence layers: the synthetic golden fixture covers deterministic runner behavior, and the historical theFPLkiwi fixture covers realistic import and scored-squad behavior. The remaining gap is the combination of those two paths: a production runner invocation using the realistic fixture.

This verification should answer a narrow question: did recent changes break the real run path for fplreview-style projection input when the input looks like converted historical theFPLkiwi data? It should not judge whether the optimizer found the best possible squad.

---

## Key Decisions

- **Completion over benchmarking:** The check should assert successful completion and a nonzero result, not a fixed final score, elapsed-time target, or optimizer-quality threshold.
- **Production path over lower-level scoring:** Existing tests already cover historical fixture import and a valid nonzero scored squad. This task should close the gap by exercising the GA runner path with that fixture.
- **Historical horizon is part of correctness:** The fplkiwi fixture starts at GW18 and covers six weeks, so verification must use that horizon rather than the default runtime horizon.

---

## Requirements

**Verification Behavior**

- R1. The verification must run the GA runner path against the committed historical theFPLkiwi fixture.
- R2. The run must use the fixture's historical projection horizon, starting at GW18 with a six-week forecast window.
- R3. The run must be bounded enough for development and test-suite use rather than invoking the production-sized search settings.
- R4. The run must complete and return a nonzero fittest score.
- R5. The run must prove the runner imports the historical fixture through the same fplreview-style projection path used by normal runtime input.

**Regression Boundaries**

- R6. The verification must not pin a final optimizer score, timing target, or optimizer-improvement expectation.
- R7. The verification must not change FPL scoring rules, GA behavior, fixture conversion, or the committed fixture contents.
- R8. The verification should avoid assertions that treat the historical theFPLkiwi fixture as official FPL state or a complete selectable-player universe.

---

## Acceptance Examples

- AE1. **Covers R1-R5.** Given the committed historical theFPLkiwi fixture, when the GA runner is invoked with a small bounded run and the GW18-GW23 horizon, then the run completes and returns a nonzero fittest score.
- AE2. **Covers R2, R5.** Given the runner loads the historical fixture, when imported player records are available during the run, then they reflect the fixture's converted fplreview-style projection columns rather than the default runtime data.
- AE3. **Covers R6-R8.** Given the verification runs successfully, when future optimizer changes alter the exact final score or elapsed time, then the check does not fail solely because of that variation.

---

## Success Criteria

- A developer can run the normal checks and know the production GA runner path still works with realistic fplkiwi-derived projection input.
- The verification complements, rather than duplicates, the existing historical fixture import and valid-squad scoring tests.
- The fixture remains framed as realistic projection input, not a benchmark or official FPL state source.

---

## Scope Boundaries

- Seeded score baselines, performance thresholds, and optimizer-quality comparisons are deferred.
- Broader benchmark suites using the historical fixture are deferred.
- Changes to scoring, transfer behavior, validity repair, mutation/crossover behavior, fixture conversion, or fixture source selection are out of scope.

---

## Dependencies / Assumptions

- The committed historical fixture remains available as `tests/fixtures/fplkiwi_historical.csv`.
- The GA runner continues to support explicit input, gameweek, forecast-window, population, generation, and seed controls.
- The existing fplreview-style importer remains the intended runtime input path for projection CSVs.

---

## Sources / Research

- Historical fixture requirements: `docs/brainstorms/2026-06-03-historical-fplkiwi-projection-fixture-requirements.md`
- Configurable runner requirements: `docs/brainstorms/2026-06-03-configurable-ga-runner-requirements.md`
- Runner implementation: `code/GA.py`
- Historical fixture tests: `tests/test_fplkiwi_historical_fixture.py`
- Runner tests: `tests/test_ga_runner.py`
