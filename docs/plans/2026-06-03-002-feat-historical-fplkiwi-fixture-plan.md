---
title: "feat: Add historical theFPLkiwi projection fixture"
type: feat
status: completed
date: 2026-06-03
origin: docs/brainstorms/2026-06-03-historical-fplkiwi-projection-fixture-requirements.md
---

# feat: Add Historical theFPLkiwi Projection Fixture

## Summary

Add one committed, season-wide historical theFPLkiwi projection fixture converted into FPLgen's existing fplreview-style CSV format. The fixture gives tests and future optimizer experiments realistic projection-row input without changing runtime import behavior or introducing score/timing benchmarks.

---

## Problem Frame

FPLgen now imports fplreview-style projection CSVs and has a compact synthetic golden fixture. That fixture is useful for wiring and characterization, but it does not expose realistic player volume, team/position distribution, prices, names, IDs, or projection quirks from public historical data.

This plan turns the brainstorm's data-fixture goal into a repeatable workflow: first verify that the chosen source can be committed, then convert a suitable historical theFPLkiwi source into the current import shape, document what was retained, and add tests that prove the fixture works as real-data-shaped import and squad input.

---

## Requirements

**Source and Fixture Contract**

- R1. The implementation selects one historical theFPLkiwi source season using explicit criteria: permission status, mapping quality, weekly projection coverage, valid-ID retention, and position/team breadth. Covers origin R5, R8-R10.
- R2. The committed fixture is one season-wide fplreview-style CSV containing nonzero theFPLkiwi source IDs only. Covers origin R1-R7.
- R3. The fixture includes the fields the existing importer already consumes: `Pos`, `ID`, `Name`, `BV`, `SV`, `Team`, and configured weekly point columns. Covers origin R3.
- R4. The implementation documents the selected season, source URL or commit, permission basis, retained row count, team coverage, position coverage, and the known absence of zero-filled selectable players. Covers origin R8-R10, R12.

**Validation**

- R5. Tests prove the historical fixture imports through `fpl.load_fplreview_players()` without special runtime behavior. Covers origin R11.
- R6. Tests prove imported rows preserve representative identity, team, price, position, and weekly projected point values. Covers origin R12-R13.
- R7. Tests prove the imported fixture has broad projection-row coverage across teams and positions. Covers origin R12.
- R8. Tests prove the fixture can reach a valid nonzero scored squad path without asserting optimizer quality, score baselines, or timing thresholds. Covers origin R14-R15.

**Non-Goals**

- R9. The implementation does not add per-gameweek replay fixtures, fplcache zero-fill pairing, runtime importer changes, seeded optimizer benchmarks, timing thresholds, or algorithm changes. Covers origin Scope Boundaries.

---

## Key Technical Decisions

- **Gate source selection before conversion:** The source and permission check comes first because a converted CSV is not useful if the repo cannot keep it. Use the `webpage` repository as the first candidate because it exposes projection data for the website and is marked Unlicense; still record the exact source path and permission basis in repo documentation.
- **Keep conversion outside runtime import:** Add a small conversion utility for maintainers/tests rather than changing `code/fpl.py`. The existing importer already accepts fplreview-style columns, so the runtime path should remain stable.
- **Commit converted fixture, not source scrape state:** The test suite should depend on a stable CSV under `tests/fixtures/`, not on live GitHub access. The converter documents provenance and can be rerun by a maintainer, but tests read committed data only.
- **Use structural GA viability, not benchmark scoring:** Reuse the golden fixture test pattern for valid-squad/nonzero-score coverage. Avoid exact optimizer scores, timing assertions, or improvement expectations.

---

## Implementation Units

### U1. Verify and Document Source Selection

- **Goal:** Choose the historical source season and document why it is suitable before adding converted data.
- **Files:**
  - `tests/fixtures/README.md`
  - `docs/plans/2026-06-03-002-feat-historical-fplkiwi-fixture-plan.md`
- **Approach:** Inspect candidate theFPLkiwi sources, starting with `theFPLkiwi/webpage` data and the shared repo's `Old_Seasons` / `FPL_projections_23_24` folders. Select the source that satisfies permission, mapping, weekly coverage, valid-ID retention, and position/team breadth. Create or update fixture documentation with source URL, commit or retrieval date, license/permission basis, chosen-season rationale, and limitations.
- **Test Scenarios:** No automated test is required for source selection itself, but documentation must be specific enough for review to verify the selected source and permission basis.
- **Verification:** A reviewer can identify the source, license/permission basis, retained-data limits, and why this season was chosen.

### U2. Add the Conversion Utility

- **Goal:** Provide a reproducible way to convert the chosen theFPLkiwi projection data into FPLgen's fplreview-style fixture shape.
- **Files:**
  - `tests/fixtures/convert_fplkiwi_fixture.py`
  - `tests/fixtures/README.md`
- **Approach:** Add a focused utility that reads the selected source CSV, filters out missing, malformed, or zero source IDs, maps source fields to `Pos`, `ID`, `Name`, `BV`, `SV`, `Team`, and weekly `*_Pts` columns, and writes a deterministic CSV. Keep source-column handling explicit and close to the utility so importer code stays untouched. The utility should report retained row count, removed source-ID count, team coverage, position coverage, and projection-week columns for documentation.
- **Test Scenarios:**
  - Given a tiny local sample with an `ID` of `0`, conversion excludes that row.
  - Given valid source rows, conversion writes fplreview-style core fields and weekly point columns.
  - Given missing source columns required for conversion, conversion fails clearly before writing an incomplete fixture.
- **Verification:** The converter can regenerate the committed fixture from the documented source input and emits the counts needed by fixture documentation.

### U3. Commit the Historical Fixture

- **Goal:** Add the converted season-wide CSV fixture as stable test input.
- **Files:**
  - `tests/fixtures/fplkiwi_historical.csv`
  - `tests/fixtures/README.md`
- **Approach:** Run the converter against the selected source, commit the converted CSV, and update fixture documentation with retained row count, team coverage, position coverage, weekly columns, invalid-ID filtering, and no-zero-fill limitation. Keep the fixture in the same CSV shape as `tests/fixtures/fplreview_golden.csv`.
- **Test Scenarios:** Covered by U4 and U5.
- **Verification:** The fixture has nonzero source IDs only, contains configured projection columns for the selected horizon, and is discoverable from fixture documentation.

### U4. Add Import and Coverage Tests

- **Goal:** Prove the historical fixture imports through the existing fplreview path and preserves representative converted values.
- **Files:**
  - `tests/test_fplkiwi_historical_fixture.py`
  - `tests/fixtures/fplkiwi_historical.csv`
- **Approach:** Add tests modeled on `tests/test_fplreview_import.py` and `tests/test_fplreview_golden.py`. Load the historical fixture through `fpl.load_fplreview_players()`, assert IDs are nonzero, assert all four positions are represented, assert broad team coverage, and inspect a small set of representative rows for identity, team, price, position, and weekly point preservation.
- **Test Scenarios:**
  - Import returns a real-data-sized player list with no missing, malformed, or zero source IDs.
  - Imported rows include all FPL positions and broad team coverage.
  - Representative known rows preserve `ID`, `Name`, `Team`, `BV`/`SV`, `Pos`, and at least one weekly points value.
- **Verification:** `python3 -m unittest discover -s tests` passes.

### U5. Add Squad/GA Viability Test

- **Goal:** Prove the historical fixture can enter FPLgen's squad-scoring path without becoming a performance benchmark.
- **Files:**
  - `tests/test_fplkiwi_historical_fixture.py`
- **Approach:** Reuse the golden fixture pattern but assert only structural success. Prefer constructing a valid 15-player squad from high enough projection rows across the imported fixture; if that is brittle after source selection, use the existing tiny seeded population path and assert only valid nonzero scored output. Do not assert exact score, runtime, generation improvement, or optimizer quality.
- **Test Scenarios:**
  - Given the historical fixture, a valid 15-player squad can be selected or generated.
  - The selected/generated squad satisfies `fpl.validteam()`, fits the budget, and returns a nonzero `fpl.scoreteam()` result.
  - The test does not depend on exact fittest score, elapsed time, or improvement across generations.
- **Verification:** The viability test passes repeatedly with the committed fixture.

### U6. Update Developer Documentation

- **Goal:** Make the historical fixture's purpose and limits visible to future maintainers.
- **Files:**
  - `README.md`
  - `tests/fixtures/README.md`
- **Approach:** Update the README's development/testing section to distinguish the synthetic golden fixture from the historical theFPLkiwi fixture. Explain that the historical fixture is realistic projection-row input, not an official FPL state snapshot or complete selectable-player universe, and that benchmark baselines remain future work.
- **Test Scenarios:** Documentation-only; covered by review.
- **Verification:** A reader can identify which fixture to use for synthetic characterization vs. realistic projection-row import/squad testing.

---

## Scope Boundaries

Deferred to follow-up work:

- Per-gameweek replay fixtures.
- Pairing with fplcache to zero-fill selectable players missing from theFPLkiwi source.
- Seeded optimizer score baselines, optimizer-quality comparisons, and timing thresholds.
- Algorithm changes based on fixture results.

Outside this feature:

- Replacing `data/fplreview.csv` as the normal runtime input.
- Treating theFPLkiwi data as official FPL state or ground-truth player availability.
- Changing `code/fpl.py` importer behavior unless source conversion reveals a current importer bug.

---

## Risks & Dependencies

- **Source permissions:** The selected source must have a documented permission basis compatible with committing converted data.
- **Source schema drift:** theFPLkiwi files may use source-specific column names. Keep mapping in the converter, not the runtime importer.
- **Filtered corpus limits:** Excluding `ID 0` rows and not zero-filling missing selectable players means the fixture is a realistic projection-row corpus, not a complete FPL universe.
- **GA fragility:** Random population tests can be seed-sensitive. Prefer deterministic known-squad construction where feasible; if using the GA, keep assertions structural.

---

## Acceptance Examples

- AE1. **Covers R1-R4.** Given the committed fixture documentation, when a maintainer reads it, then they can identify the selected source, permission basis, row-retention counts, team/position coverage, and no-zero-fill limitation.
- AE2. **Covers R5-R7.** Given the committed historical fixture, when tests load it with `fpl.load_fplreview_players()`, then import succeeds, all IDs are nonzero source IDs, positions and teams have broad coverage, and representative rows preserve converted values.
- AE3. **Covers R8-R9.** Given the historical fixture, when the squad viability test runs, then it reaches a valid nonzero scored squad path without asserting exact score, timing, or optimizer improvement.

---

## Sources & Research

- Origin requirements: `docs/brainstorms/2026-06-03-historical-fplkiwi-projection-fixture-requirements.md`
- Existing synthetic fixture plan: `docs/plans/2026-06-02-002-feat-golden-fplreview-fixture-plan.md`
- Existing importer and tests: `code/fpl.py`, `tests/test_fplreview_import.py`, `tests/test_fplreview_golden.py`, `tests/test_ga_runner.py`
- theFPLkiwi webpage repo: `https://github.com/theFPLkiwi/webpage`
- theFPLkiwi shared repo: `https://github.com/theFPLkiwi/theFPLkiwi`
- fplreview export docs: `https://docs.fplreview.com/the-model/planner-interface/export_projections/`
- fplreview upload docs: `https://docs.fplreview.com/the-model/planner-interface/upload_projections/`
