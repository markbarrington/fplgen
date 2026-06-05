---
title: "test: Verify fplkiwi production runner path"
type: test
status: completed
date: 2026-06-03
origin: docs/brainstorms/2026-06-03-fplkiwi-production-path-verification-requirements.md
---

# test: Verify FPLkiwi Production Runner Path

## Summary

Add a lightweight runner verification that uses the committed historical theFPLkiwi fixture as realistic fplreview-style input. The verification should prove a bounded GA runner invocation completes on the GW18-GW23 projection horizon and returns a nonzero result without introducing score or timing benchmarks.

## Problem Frame

FPLgen already has two nearby safety nets: runner behavior is covered with the synthetic golden fixture, and the fplkiwi fixture is covered through import and known-squad scoring. What is still missing is the combination of those concerns: using the production runner path with realistic fplkiwi-derived projection input.

This plan keeps the work test-oriented. It should raise confidence that normal runtime wiring still works, while preserving the fixture's current role as realistic projection input rather than treating it as official FPL state or an optimizer-quality benchmark.

## Requirements

**Runner Verification**

- R1. The test suite verifies that the GA runner can load `tests/fixtures/fplkiwi_historical.csv` through the existing fplreview-style import path. Covers origin R1, R5.
- R2. The verification uses the fixture's historical GW18-GW23 projection horizon. Covers origin R2.
- R3. The verification uses bounded runner settings suitable for normal development checks. Covers origin R3.
- R4. The verification asserts successful completion and a nonzero fittest score. Covers origin R4.
- R5. The verification checks enough imported runner state to show the fplkiwi fixture was actually loaded, not the default runtime input. Covers origin R5.

**Regression Boundaries**

- R6. The verification does not assert an exact final score, elapsed time, or optimizer improvement. Covers origin R6.
- R7. The implementation does not change scoring rules, GA behavior, fixture conversion, or fixture contents. Covers origin R7.
- R8. The verification does not treat the fplkiwi fixture as official FPL state or a complete selectable-player universe. Covers origin R8.

## Key Technical Decisions

- **Extend runner tests instead of adding a new benchmark harness:** `tests/test_ga_runner.py` already isolates runner state, temporary inspection output, stdout capture, random state restoration, and bounded runs. Extending that pattern covers the missing production-path confidence with the least new surface.
- **Use fixture-specific horizon controls:** The fplkiwi fixture starts at GW18 and covers six weeks, so the test should pass explicit gameweek and forecast controls rather than relying on FPLgen's default runtime horizon.
- **Assert structural success only:** The test should assert completion, nonzero score, expected generation bound, and fplkiwi-loaded player state. Exact score, elapsed time, and optimizer-improvement assertions remain out of scope.

## Implementation Units

### U1. Add FPLkiwi Runner Verification

- **Goal:** Verify that the production GA runner path completes against the historical fplkiwi fixture with bounded development settings.
- **Requirements:** R1-R8
- **Dependencies:** None
- **Files:**
  - `tests/test_ga_runner.py`
  - `tests/fixtures/fplkiwi_historical.csv`
- **Approach:** Add a dedicated fplkiwi fixture path next to the existing golden fixture path in the runner tests. Follow the current runner-test structure: patch `fpl_module.data_file` to a temporary data directory, capture stdout, use a small population and short generation limit, seed randomness, and restore module state in teardown. Invoke `ga_module.run()` with the fplkiwi fixture and explicit GW18 / six-week horizon. Assert a nonzero fittest score and the configured generation bound without recording a golden score.
- **Execution note:** Implement this as a characterization-style test first; it should describe current runner behavior without changing production code unless the test exposes a real bug.
- **Patterns to follow:** Existing `GARunnerTests` setup/teardown and stdout capture in `tests/test_ga_runner.py`; historical horizon setup in `tests/test_fplkiwi_historical_fixture.py`.
- **Test scenarios:**
  - Covers AE1. Given the committed fplkiwi fixture, when the runner executes with a small population, short generation limit, seed, gameweek 18, and six forecast weeks, then it completes and returns a nonzero fittest score.
  - Covers AE2. Given the fplkiwi runner invocation, when imported player state is inspected after the run, then representative fplkiwi player data is present and the fixture-specific projection horizon was used.
  - Covers AE3. Given the runner output varies under future optimizer changes, when the final score remains nonzero and the run completes within the configured generation bound, then the test does not fail solely because the exact score changed.
- **Verification:** The normal unit test discovery path passes, and the new test fails if the runner cannot load or execute against the fplkiwi fixture.

### U2. Keep Documentation Aligned

- **Goal:** Make sure the project documentation still describes the fplkiwi fixture's verification role accurately after adding runner coverage.
- **Requirements:** R6-R8
- **Dependencies:** U1
- **Files:**
  - `README.md`
  - `tests/fixtures/README.md`
- **Approach:** Review the current fixture documentation after adding the runner test. Update only if needed to mention that the historical fplkiwi fixture now also has bounded runner-path coverage. Preserve the existing warning that it is realistic projection input, not official FPL state or a benchmark dataset.
- **Patterns to follow:** Existing concise fixture descriptions in `README.md` and `tests/fixtures/README.md`.
- **Test scenarios:** Test expectation: none -- documentation alignment is verified by review; behavior is covered by U1.
- **Verification:** A reader can distinguish the golden fixture's deterministic characterization role from the fplkiwi fixture's realistic projection-input verification role.

## Scope Boundaries

### In Scope

- A bounded runner-path verification using the committed fplkiwi fixture.
- Explicit GW18-GW23 horizon controls for that verification.
- Structural assertions for completion, nonzero score, and fplkiwi-loaded state.
- Small documentation alignment only if the new coverage changes what the docs should say.

### Deferred to Follow-Up Work

- Seeded score baselines and optimizer-quality comparisons.
- Runtime or CI performance thresholds.
- Broader benchmark suites using the historical fixture.

### Out of Scope

- Changes to scoring, transfer behavior, validity repair, mutation/crossover behavior, fixture conversion, fixture contents, or fixture source selection.
- Treating the historical fplkiwi fixture as official FPL state or a complete selectable-player universe.

## Risks & Dependencies

- **Search fragility:** Very small GA settings may fail to find a valid nonzero squad for a large realistic fixture under some seeds. Pick a stable bounded configuration during implementation, but keep the assertion structural rather than score-specific.
- **Global state leakage:** Runner tests mutate module-level gameweek, forecast, players, fixtures, data-file, and random state. Reuse the existing teardown pattern so the fplkiwi case does not leak state into adjacent tests.
- **Fixture horizon mismatch:** The fixture starts at GW18, so forgetting explicit horizon controls should fail quickly rather than silently testing the wrong projection columns.

## Acceptance Examples

- AE1. **Covers R1-R4.** Given the committed historical fplkiwi fixture, when the runner is invoked with bounded settings and the GW18-GW23 horizon, then the run completes and returns a nonzero fittest score.
- AE2. **Covers R2, R5.** Given the runner loads the historical fixture, when imported player state is inspected after the run, then representative fplkiwi fixture values are present rather than default runtime data.
- AE3. **Covers R6-R8.** Given future optimizer changes alter the exact final score or elapsed time, when the run still completes with a nonzero result, then this verification does not fail solely because of that variation.

## Sources & Research

- Origin requirements: `docs/brainstorms/2026-06-03-fplkiwi-production-path-verification-requirements.md`
- Runner implementation: `code/GA.py`
- Existing runner tests: `tests/test_ga_runner.py`
- Historical fixture tests: `tests/test_fplkiwi_historical_fixture.py`
- Historical fixture documentation: `tests/fixtures/README.md`
- Related runner plan: `docs/plans/2026-06-03-001-feat-configurable-ga-runner-plan.md`
- Related fplkiwi fixture plan: `docs/plans/2026-06-03-002-feat-historical-fplkiwi-fixture-plan.md`
