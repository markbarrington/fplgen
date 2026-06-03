# Test Fixtures

## `fplreview_minimal.csv`

Small importer fixture for focused fplreview column-mapping and validation tests.

## `fplreview_golden.csv`

Synthetic fplreview-style fixture with enough players to prove import, known-squad scoring, and a tiny seeded GA smoke path. This is validation data, not a real projection-quality sample.

## `fplkiwi_historical.csv`

Historical projection-row fixture converted from theFPLkiwi data into FPLgen's fplreview-style CSV shape.

- Source: `https://github.com/theFPLkiwi/webpage/blob/main/data/Projected_FPL_2324.csv`
- Source blob SHA from GitHub contents API: `27955c52cee1d90403cccae2efc80fd1f1e0e5b5`
- Source CSV SHA-256: `416414b9a422afc484b2db0d4abf2c1994ceb931793dd403705e1d71879382ab`
- Source license: Unlicense in `https://github.com/theFPLkiwi/webpage/blob/main/LICENSE`
- Selected horizon: GW18-GW23, exposed as `18_Pts` through `23_Pts`
- Rows retained: 461
- Rows skipped for missing, malformed, or zero source ID: 0
- Team coverage: 20 teams
- Position coverage: 39 GKP, 165 DEF, 202 MID, 55 FWD

The source was selected because it is a single season-wide public CSV from theFPLkiwi, has an explicit permission basis through the Unlicense, maps cleanly to FPLgen's fplreview-style fields, and gives broad position/team coverage. The source begins at GW18 rather than FPLgen's default GW3, so tests that import this fixture set the runtime horizon to GW18-GW23 before loading it.

This fixture intentionally keeps only rows with nonzero theFPLkiwi source IDs. It does not validate those IDs against an official FPL bootstrap snapshot, does not zero-fill selectable FPL players missing from the source, and should not be treated as a complete official FPL player universe.

To regenerate:

```sh
curl -L https://raw.githubusercontent.com/theFPLkiwi/webpage/main/data/Projected_FPL_2324.csv -o /tmp/Projected_FPL_2324.csv
python3 - <<'PY'
import hashlib
from pathlib import Path

expected = "416414b9a422afc484b2db0d4abf2c1994ceb931793dd403705e1d71879382ab"
actual = hashlib.sha256(Path("/tmp/Projected_FPL_2324.csv").read_bytes()).hexdigest()
if actual != expected:
    raise SystemExit("source checksum mismatch: %s" % actual)
PY
python3 tests/fixtures/convert_fplkiwi_fixture.py /tmp/Projected_FPL_2324.csv tests/fixtures/fplkiwi_historical.csv --start-week 18 --forecast-weeks 6
```
