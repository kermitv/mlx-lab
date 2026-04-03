# MLX Control Module Status

## Current Phase

Phase 1: complete.

## Completed Items

- Branch model established for the workstream.
- Workstream identity established as the MLX Control Module.
- Active implementation branch fixed to `feature/mlx-control-phase0`.
- Evidence branch isolated from active feature work.
- Phase 0 documentation and package scaffold created.
- Phase 0 scaffold review baseline established.
- Phase 1 typed contracts established for the `mlx_control` Python surface.
- Phase 1 validation invariants established for core control-module inputs and state shapes.
- Phase 1 ergonomic constructors added for the controller-facing objects.
- Phase 1 read-only controller methods implemented.
- Phase 1 mutation entry points reduced to stubs only, with no runtime/process control behavior introduced.

## In Progress

- Phase 1 closeout is complete. Remaining work is Phase 2 planning and benchmark integration design.

## Next Milestone

Plan Phase 2 and design benchmark integration so `benchmark_harness` can consume `mlx_control` without reversing the dependency direction.

## Risks / Drift Watch

- Benchmark leakage into the control-module design before Phase 2.
- Shell-first drift that bypasses a Python-first public surface.
- Premature integrations for external tools before the local baseline is stable.
- Weak or split state ownership across multiple modules.
- Documentation lagging behind implementation changes.
- Evidence contamination from the blocked `exp/gemma4-mlx-day0` lane.
- Runtime/process control behavior is still not implemented and must not be implied by the current API surface.

## Branch Context

- Active branch: `feature/mlx-control-phase0`
- Workstream: MLX Control Module
- Governance posture: supervised and phase-tracked
- Blocked lane: `exp/gemma4-mlx-day0` is not part of the active implementation path
- Dependency rule: `benchmark_harness -> mlx_control`
