---
date: 2026-06-03
topic: historical-fplkiwi-projection-fixture
status: completed
pr: https://github.com/markbarrington/fplgen/pull/7
---

# Historical theFPLkiwi Projection Fixture Requirements

## Summary

Add a committed, season-wide historical projection fixture converted from theFPLkiwi into fplreview-style CSV shape. The fixture should provide a realistic theFPLkiwi projection-row corpus for FPLgen functionality testing and future algorithm-performance experiments.

---

## Problem Frame

FPLgen now supports fplreview-style projection imports and has a synthetic golden fixture that proves the current import-to-scoring path works. That fixture is intentionally compact and artificial, so it does not exercise the real player count, naming, ID, position, team, price, and projection quirks that appear in public historical projection data.

The next useful step is a realistic historical projection corpus that can be committed to the repo and reused by tests. For this first version, the data should be useful as benchmark input, not as a complete selectable FPL universe or a full benchmark suite with score or timing thresholds.

---

## Key Decisions

- **Use one season-wide CSV.** The fixture should represent one historical season in a single fplreview-style CSV rather than a set of per-gameweek snapshots. This covers the current regression and benchmark-input need with much less fixture management.
- **Keep only nonzero theFPLkiwi projection rows.** Rows with nonzero source IDs are in scope. Validating those IDs against official FPL state and adding synthetic zero-projection rows for selectable players missing from theFPLkiwi source are deferred.
- **Treat performance as future-facing.** The first fixture should make realistic algorithm runs possible, but it should not introduce pass/fail optimizer-performance thresholds yet.
- **Choose the strongest available historical source.** The implementation can choose the historical theFPLkiwi season during planning, with 2022/23 or 2023/24 as likely candidates, but the choice should be based on permission status, mapping quality, weekly projection coverage, valid-ID retention, and position/team breadth rather than download convenience alone.

---

## Requirements

**Fixture Shape**

- R1. Add one committed historical projection CSV converted from theFPLkiwi into the fplreview-style format FPLgen already imports.
- R2. The fixture must represent a season-wide projection table rather than separate weekly snapshot files.
- R3. The fixture must include the player identity and squad-building fields needed by FPLgen's existing fplreview importer: position, FPL ID, player name, buy value, sell value, team, and weekly projected points.
- R4. The fixture must include enough valid rows to behave like a realistic theFPLkiwi projection-row corpus for import and GA input tests, not just a hand-picked legal squad.

**Source Data Handling**

- R5. The fixture must be derived from public historical theFPLkiwi projection data.
- R6. Rows with missing, malformed, or zero theFPLkiwi source IDs must be excluded from the committed fixture.
- R7. Missing selectable FPL players that do not appear in the chosen theFPLkiwi source must not be zero-filled in this first version.
- R8. The selected source must have a license or permission basis compatible with committing converted fixture data to this repo.
- R9. The chosen season must be selected using explicit criteria: clear permission status, stable mapping to the fplreview-style fields, enough weekly projection columns for FPLgen's configured horizon, high valid-ID retention after filtering, and broad position/team coverage.
- R10. The chosen season must be documented clearly enough that a future maintainer can identify the source season, understand how it satisfied the selection criteria, and verify the permission basis for committing the converted fixture.

**Validation**

- R11. Tests must prove the historical fixture imports through the existing fplreview import path without special runtime behavior.
- R12. Tests must assert that imported fixture data contains realistic breadth across positions and teams, and fixture documentation must record retained row count, team coverage, position coverage, and the known absence of zero-filled selectable players.
- R13. Tests must assert that weekly projected point values survive conversion into FPLgen's internal player records.
- R14. Tests must prove the fixture can be used as squad or GA input by reaching at least one valid nonzero scored squad path.
- R15. Tests may use the fixture as input for future algorithm checks, but this first version must not require seeded score baselines, timing thresholds, or optimizer-improvement assertions.

---

## Acceptance Examples

- AE1. **Covers R1-R4, R11.** Given the committed historical fixture, when the existing fplreview import helper loads it, then import succeeds and returns a realistic multi-position player pool.
- AE2. **Covers R5-R7.** Given a theFPLkiwi source row has FPL ID `0` or another invalid ID, when the fixture is created, then that row is not present in the committed fplreview-style CSV.
- AE3. **Covers R8-R10.** Given the converted fixture is committed, when a maintainer checks the fixture documentation, then it identifies the source season, explains how it met the selection criteria, and cites the permission basis for committing the converted data.
- AE4. **Covers R12-R13.** Given the imported fixture contains known players from the selected season, when tests inspect representative rows, then position, team, price, and weekly point values match the converted fixture data.
- AE5. **Covers R14.** Given the imported historical fixture, when a test constructs or generates a valid 15-player squad from it, then FPLgen can score that squad with a nonzero result.
- AE6. **Covers R15.** Given the historical fixture exists, when the test suite runs, then it does not fail because a seeded optimizer score, timing threshold, or performance baseline changed.

---

## Success Criteria

- A developer can run the normal test suite and know the real-data-shaped fplreview import path still works.
- A future algorithm-performance effort can reuse the fixture as realistic projection-row input without first inventing or sourcing its own player corpus.
- The fixture's limitations are explicit: it is historical theFPLkiwi projection data with invalid IDs removed, not a complete selectable FPL universe.

---

## Scope Boundaries

Deferred for later:

- Per-gameweek replay fixtures that model point-in-time projection snapshots.
- Pairing with fplcache data to add zero-projection rows for selectable players missing from theFPLkiwi source.
- Seeded GA score baselines, optimizer-quality comparisons, and timing thresholds.
- Algorithm changes based on fixture results.

Outside this fixture's purpose:

- Replacing fplreview.com exports as the normal runtime input.
- Treating theFPLkiwi projections as official FPL state or ground-truth player availability.

---

## Dependencies / Assumptions

- A suitable public historical theFPLkiwi CSV is available and can be converted without excessive interpretation.
- The existing fplreview importer remains the intended import path for projection CSVs.

---

## Sources / Research

- Repo improvement idea: `docs/ideation/2026-06-02-repo-improvements-ideation.md`
- Prior fplreview import requirements: `docs/brainstorms/2026-06-02-fplreview-import-requirements.md`
- Prior golden fixture requirements: `docs/brainstorms/2026-06-02-golden-fplreview-fixture-requirements.md`
- theFPLkiwi repository: `https://github.com/theFPLkiwi/theFPLkiwi`
- theFPLkiwi webpage repository: `https://github.com/theFPLkiwi/webpage`
