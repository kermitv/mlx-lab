# MLX Control Module PRD

## Purpose

`mlx_control` is an internal Python-first module for owning control-plane concerns around local MLX model lifecycle, state, health, registry, and configuration posture inside this repository.

## Status

Phase 0: documentation, boundary definition, and package scaffold only.

No runtime behavior is implemented in this phase.

## Goals

- Establish a small, explicit internal module boundary for control-plane work.
- Keep the public control surface Python-first from the start.
- Define a single ownership point for active MLX control state.
- Keep benchmark integration downstream of the control module.
- Preserve an extraction-safe package shape without committing to extraction yet.

## In-Scope Capabilities

- Internal module layout for controller, state, health, registry, and config concerns.
- Architectural documentation for dependency direction and phase sequencing.
- Placeholder Python files for the future package surface.
- Governance tracking for current phase, drift risks, and branch posture.

## Non-Goals

- No runtime control logic.
- No CLI.
- No daemon or service mode.
- No HTTP API.
- No benchmark-specific feature design.
- No OpenClaw, Codex, or other external tool abstractions.
- No work related to the blocked `exp/gemma4-mlx-day0` experiment.

## Architectural Boundary

`mlx_control` owns the internal control-module boundary.

The dependency rule for this workstream is:

`benchmark_harness -> mlx_control`

The reverse dependency is not allowed. Benchmark code may consume the control module later, but `mlx_control` must not import or depend on benchmark code, benchmark configuration, or run artifacts.

## Future Extraction Posture

The module should be structured so it can be extracted later if reuse is proven, but extraction is a Phase 4 decision rather than a Phase 0 assumption.

Extraction-safe posture means:

- clear package responsibilities
- minimal repo-specific leakage
- explicit state ownership
- Python-first interfaces before secondary surfaces

## Intended Phase 1 API Surface

These are intended interface targets only for Phase 1 refinement. They are not implemented behavior in Phase 0, and the exact signatures, return types, and object model remain subject to Phase 1 design review.

- `start(model_id)`
- `stop()`
- `switch(model_id)`
- `status()`
- `active_model()`
- `health()`
- `list_models()`

## Design Principles

- Internal-first before externalization.
- Python-first before shell-first.
- Single state owner before distributed state inference.
- Small boundary before broad integration.
- Benchmark consumption of control, never control consumption of benchmarks.
- Extraction-safe design now, extraction decision later.
