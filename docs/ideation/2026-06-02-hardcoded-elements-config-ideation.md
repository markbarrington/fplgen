---
date: 2026-06-02
topic: hardcoded-elements-configuration
focus: conceptual options for making FPLgen runs simpler and more flexible
mode: repo-grounded
---

# Ideation: Hardcoded Elements and Configuration in FPLgen

## Grounding Context

FPLgen currently requires source edits for routine run changes. The most visible hardcoded elements are the runtime input path, gameweek and forecast window, GA population and generation controls, FPL squad/rule constants, chip flags, current-team and transfer behavior, team mappings, inspection output, and several global state variables in `fpl.py`.

The project is small enough that a heavy configuration platform would be premature, but it has crossed the line where source edits are the normal control surface. The design question is not just "where do constants live?" but "what kind of user workflow should a run have?"

## Ranked Options

### 1. CLI-First Runtime Options

Add a command-line runner where common run choices are passed as flags: input CSV, output path, gameweek, forecast weeks, population size, generation limit, seed, and verbose output.

This is the best first move because it directly removes source edits from day-to-day use while keeping the project simple. It also gives tests a deterministic way to run tiny optimizer jobs.

### 2. Config File Per Scenario

Support a checked-in or user-created config file such as `config/default.toml` or `runs/example.toml`. The file would hold run parameters, FPL rules, chip settings, current squad, and output choices.

This is better than CLI flags for repeatable scenarios. It lets Mark keep several named configurations: conservative run, wildcard run, short test run, current gameweek run, and so on.

### 3. Hybrid CLI Plus Config File

Use a config file for structured settings and allow CLI flags to override selected values. For example: `fplgen --config runs/gw12.toml --seed 7 --generations 50`.

This is probably the best end-state. It keeps repeatable scenarios clean but still supports quick experiments without editing files.

### 4. Typed `RunConfig` Object

Introduce a single in-memory configuration object and pass it into import, scoring, and GA execution. This object would own gameweek, forecast weeks, transfer weeks, budget, squad rules, chip flags, and paths.

This is the architectural unlock. CLI and config files are just input surfaces; a `RunConfig` prevents the rest of the code from continuing to read globals.

### 5. `FplContext` for Run State

Move mutable run state into a context object: players, fixtures, bank, team mappings, current squad, and derived scoring inputs. Methods that currently read module globals would receive or live on this context.

This is more invasive than `RunConfig`, but it is the cleanest way to support multiple runs, tests, and future workflows without state leaking between them.

### 6. Scenario Files for FPL-Specific Choices

Separate "how the optimizer should run" from "what FPL situation am I in?" A scenario file could include current squad, bank, free transfers, chips available, gameweek, transfer horizon, excluded players, and any manual player locks.

This would match the real mental model of using the tool: each run is not merely a technical execution, it is an FPL decision scenario.

### 7. Presets With Minimal Setup

Provide named presets such as `quick`, `standard`, `deep`, `wildcard`, and `test`. Presets can be built into the CLI or stored as config files.

This lowers friction, especially while the project is still evolving. It also avoids making every setting feel equally important to the user.

### 8. Data-Driven Rules

Move FPL rules into data: squad shape, budget, max players per club, formation constraints, chip availability, and transfer behavior.

This is valuable if rules change or historical seasons matter, but it should come after the runner and config shape are stable. Otherwise it risks over-abstracting before the real workflow is clear.

## Rejected or Deferred Ideas

| Idea | Reason |
|---|---|
| Environment variables as the main interface | Useful for CI or secrets, but poor for an FPL scenario with many structured values. |
| Editing a generated Python settings file | Removes edits from core source but still makes configuration feel like programming. |
| Database-backed configuration | Too heavy for the current project shape. |
| Web UI first | Attractive eventually, but the underlying run/config boundary should come first. |
| Full rewrite around a new framework | The repo can get much more flexible through staged changes. |

## Recommendation

The best path is staged:

1. Add a CLI runner for the obvious knobs.
2. Introduce a `RunConfig` object so those knobs stop being globals.
3. Add scenario/config files once the shape of the knobs is proven.
4. Move mutable state into an `FplContext`.
5. Add presets and richer scenario files for normal FPL workflows.

This sequence removes source edits early without forcing a large architecture rewrite up front.
