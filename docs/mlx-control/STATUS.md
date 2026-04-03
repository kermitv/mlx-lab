# MLX Control Module Status

## Current Phase

Phase 0: PRD, architecture, scope, and scaffold.

## Completed Items

- Branch model established for the workstream.
- Workstream identity established as the MLX Control Module.
- Active implementation branch fixed to `feature/mlx-control-phase0`.
- Evidence branch isolated from active feature work.
- Phase 0 documentation and package scaffold created.
- Phase 0 scaffold review baseline established.

## In Progress

- Phase 0 is complete. Remaining work is transition setup for Phase 1 interface definition.

## Next Milestone

Define the Phase 1 Python-first interface surface for `mlx_control` without introducing runtime control behavior.

## Risks / Drift Watch

- Benchmark leakage into the control-module design before Phase 2.
- Shell-first drift that bypasses a Python-first public surface.
- Premature integrations for external tools before the local baseline is stable.
- Weak or split state ownership across multiple modules.
- Documentation lagging behind implementation changes.
- Evidence contamination from the blocked `exp/gemma4-mlx-day0` lane.

## Branch Context

- Active branch: `feature/mlx-control-phase0`
- Workstream: MLX Control Module
- Governance posture: supervised and phase-tracked
- Blocked lane: `exp/gemma4-mlx-day0` is not part of the active implementation path
