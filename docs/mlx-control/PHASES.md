# MLX Control Module Phases

## Phase 0

Objective: lock the governance stance, package boundary, and documentation baseline.

Scope:

- PRD
- architecture definition
- phase plan
- status tracking
- decision log
- placeholder package and test scaffold

Success criteria:

- required Phase 0 docs exist
- requested `src/mlx_control/` scaffold exists
- requested `tests/test_mlx_control/` scaffold exists
- dependency direction is documented consistently as `benchmark_harness -> mlx_control`
- no runtime behavior is introduced

## Phase 1

Objective: establish the initial Python-first control API and canonical state owner.

Scope:

- define controller-facing Python objects
- define state ownership model
- define config and health model shapes
- local unit coverage for the Python surface

Success criteria:

- a minimal Python-first control surface exists
- state ownership is explicit and singular
- no CLI or service mode is required for core usage
- tests validate core control-module contracts locally

## Phase 2

Objective: integrate benchmark consumption of the control module without reversing the dependency direction.

Scope:

- benchmark harness reads from `mlx_control`
- adapter or integration layer as needed
- benchmark-facing usage patterns validated against the package boundary

Success criteria:

- benchmark harness consumes `mlx_control` without imports in the reverse direction
- benchmark-specific concerns remain outside the core module where practical
- boundary remains small and reviewable

## Phase 3

Objective: evaluate broader tool and operator surfaces after the local Python baseline is stable.

Scope:

- optional CLI
- optional service mode
- optional adapters for external tools
- hardening of health and registry surfaces

Success criteria:

- Phase 1 and Phase 2 are stable first
- new interfaces do not fragment state ownership
- public surface expansion is justified by proven usage

## Phase 4

Objective: decide whether extraction is warranted.

Scope:

- reuse review
- packaging posture review
- interface stability review
- extraction cost versus value analysis

Success criteria:

- extraction decision is based on demonstrated reuse
- repository-local assumptions are understood and documented
- extraction, if approved, does not require major boundary redesign
