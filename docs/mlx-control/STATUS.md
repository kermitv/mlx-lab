# MLX Control Module Status

## Current Phase

Phase 3B: complete.

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
- Phase 2 benchmark integration pattern documented and approved.
- Phase 2 benchmark-side adapter established under `benchmark_harness/integrations/mlx_control.py`.
- Phase 2 read-only preflight interpretation layer established for benchmark consumption.
- Phase 2 adopted one real harness preflight path that consumes the benchmark-side MCM adapter.
- Phase 3A repo-local CLI utility established as the first controlled local tool consumer.
- Phase 3A `mlx-control status` command surface implemented as a read-only repo-local CLI entrypoint.
- Phase 3A CLI-side adapter established under `tools/integrations/mlx_control.py`.
- Phase 3A CLI can construct a real read-only controller snapshot from repo-local benchmark visibility artifacts.
- Phase 3B OpenCode-facing read-only adapter established under `tools/integrations/opencode_mlx_control.py`.
- Phase 3B OpenCode-facing status/readiness interpretation established as consumer-local logic outside `src/mlx_control/`.
- Phase 3B adopted one real repo-local consumer path that uses the OpenCode-facing adapter through `mlx-control status`.

## In Progress

- Phase 3B closeout is complete.
- Remaining work is deciding whether another controlled adopter is warranted after the repo-local CLI and OpenCode slices.

## Next Milestone

Decide whether another controlled adopter is warranted and, if so, scope it without breaking the proven tool boundary or introducing runtime/process control.

## Risks / Drift Watch

- Benchmark-specific convenience pressure reshaping the core control-module boundary after Phase 2.
- Benchmark adapter sprawl that bypasses the documented integration boundary.
- CLI convenience pressure bypassing `MLXController` and reintroducing direct state peeking.
- Next-adopter integration bypassing the proven repo-local tool boundary `tools -> tools.integrations.mlx_control -> mlx_control`.
- OpenCode-facing readiness logic drifting into core MCM instead of staying consumer-local.
- Premature additional-adopter work before the current repo-local CLI and OpenCode pattern is judged sufficient.
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
- Tool boundary: `tools -> tools.integrations.mlx_control -> mlx_control`
- Planned OpenCode adapter: `tools/integrations/opencode_mlx_control.py`
