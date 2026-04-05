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
- add validation invariants and ergonomic constructors
- expose read-only controller methods
- keep mutation methods as non-runtime stubs only

Success criteria:

- a minimal Python-first control surface exists
- state ownership is explicit and singular
- typed contracts define the controller-facing API
- validation invariants protect core control-module contracts locally
- ergonomic constructors support the intended Python-first usage
- read-only controller methods are available without requiring runtime control behavior
- mutation surfaces exist only as stubs
- no CLI or service mode is required for core usage
- tests validate core control-module contracts locally

Status:

- complete
- runtime/process control is explicitly not implemented in this phase

## Phase 2

Objective: plan and design benchmark consumption of the control module without reversing the dependency direction.

Scope:

- Phase 2 integration plan and review baseline
- benchmark harness reads from `mlx_control`
- adapter or integration layer as needed
- benchmark-facing usage patterns validated against the package boundary
- benchmark integration design that preserves `benchmark_harness -> mlx_control`
- explicit separation from runtime/process control implementation
- explicit responsibility split between core control concerns and benchmark-only concerns
- recommended repository-local placement for benchmark adapter code
- minimal benchmark-side adapter implementation for read-only preflight consumption
- one real harness preflight adoption slice that consumes the adapter

Success criteria:

- a reviewed integration plan exists for benchmark adoption
- benchmark harness consumes `mlx_control` without imports in the reverse direction
- benchmark-specific concerns remain outside the core module where practical
- boundary remains small and reviewable
- runtime/process control remains a separate follow-on concern unless intentionally re-scoped
- a concrete adapter placement is documented without requiring runtime implementation
- a benchmark-side adapter exists for read-only preflight usage
- at least one real harness preflight path consumes the adapter rather than re-encoding the same checks inline

Status:

- complete
- delivered a thin downstream adapter layer in `benchmark_harness`, not benchmark behavior in `mlx_control`
- delivered a read-only benchmark preflight interpretation layer over `MLXController`
- delivered one real harness preflight adoption slice
- runtime/process control remains explicitly not implemented in this phase

## Phase 3

Objective: evaluate broader tool and operator surfaces after the local Python baseline is stable.

Scope:

- optional CLI
- optional service mode
- optional adapters for external tools
- hardening of health and registry surfaces
- Phase 3A selects one controlled first local consumer before broader tool adoption
- first consumer is a repo-local CLI utility
- OpenCode is deferred as a likely second adopter
- OpenClaw is explicitly deferred until the local tool boundary is proven
- recommended placement for the first tool adapter is `tools/integrations/mlx_control.py`
- recommended placement for the first CLI entrypoint is `tools/mlx_control_cli.py`
- first approved command surface is `mlx-control status`
- Phase 3A remains read-only and does not implement runtime/process control
- Phase 3B selects OpenCode as the next controlled adopter after the repo-local CLI
- OpenClaw remains explicitly deferred as a comparison point, not an implementation target
- recommended Phase 3B placement is `tools/integrations/opencode_mlx_control.py`
- the first approved Phase 3B slice is a read-only OpenCode-facing status/readiness adapter
- Phase 3B remains read-only and does not implement runtime/process control, provider switching, endpoint probing, or subprocess behavior
- OpenCode-facing code must consume `MLXController` rather than peeking into `mlx_control.state` or inventing a second state source
- one real repo-local consumer path uses the OpenCode-facing adapter

Success criteria:

- Phase 1 and Phase 2 are stable first
- new interfaces do not fragment state ownership
- public surface expansion is justified by proven usage
- the first local tool consumer is documented with explicit sequencing and deferrals
- the first implementation slice is small, read-only, and controller-bound
- the first approved command surface exists as a repo-local CLI
- the CLI can obtain a real read-only controller snapshot from repo-local context without moving controller construction into `src/mlx_control/`
- a read-only OpenCode-facing status/readiness adapter exists under the documented repo-local placement
- at least one real repo-local consumer path uses the OpenCode-facing adapter without introducing a second state source

Status:

- Phase 3A complete
- first controlled Phase 3A consumer is a repo-local CLI utility
- delivered `tools/mlx_control_cli.py` as the first repo-local CLI entrypoint
- delivered `tools/integrations/mlx_control.py` as the CLI-side adapter boundary
- delivered `mlx-control status` as the first approved command surface
- delivered a real read-only controller-loading path from repo-local benchmark visibility artifacts
- Phase 3B complete
- OpenCode adopted as the next controlled consumer through a read-only adapter slice
- delivered `tools/integrations/opencode_mlx_control.py` as the OpenCode-facing adapter boundary
- delivered consumer-local OpenCode readiness logic outside `src/mlx_control/`
- delivered one real repo-local consumer path that uses the OpenCode-facing adapter through `mlx-control status`
- OpenClaw remains explicitly deferred due to higher blast radius
- runtime/process control remains explicitly not implemented in this phase

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
