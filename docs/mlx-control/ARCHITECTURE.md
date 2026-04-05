# MLX Control Module Architecture

## Module Boundary

`mlx_control` is the internal control-plane package for MLX lifecycle coordination inside this repository.

Phase 1 established typed contracts, validation invariants, ergonomic constructors, read-only controller methods, and mutation stubs only.

Future runtime work should remain inside `src/mlx_control/` unless there is a clear reason to place repository-specific adapters elsewhere.

## Dependency Direction

Required dependency direction:

`benchmark_harness -> mlx_control`

Not allowed:

- `mlx_control -> benchmark_harness`
- imports from benchmark run directories into `mlx_control`
- control design driven directly by benchmark-only shortcuts

## Package Responsibility Split

- `controller.py`: control-plane entry point and orchestration surface
- `state.py`: canonical ownership of active control state
- `health.py`: health model and future health-check surface
- `registry.py`: model and resource registration abstractions
- `config.py`: control-module configuration model and loading posture
- `__init__.py`: package export surface for Phase 1 contracts

## State Ownership

State ownership belongs to `mlx_control.state`.

Future code should treat this module as the single source of truth for active model state and related controller-visible state. Benchmark code and other downstream consumers should read through the control surface rather than infer state independently.

## Runtime Boundary Assumption

The Phase 1 baseline targets single-machine local MLX control only.

This baseline excludes remote orchestration semantics, cross-host coordination, distributed control, and network-topology-aware runtime assumptions. If remote control is considered later, it should be treated as a separate interface expansion rather than baked into the initial local control model.

## State Categories

The intended control-state model distinguishes between the following categories:

- desired state: the control module's requested target posture, such as the model intended to be active
- observed runtime state: the currently observed local runtime condition as seen from the control module
- active model identity: the single canonical identity of the model considered active for control and downstream consumers
- health state: the summarized health assessment of the local control target and related serving posture

## Likely Future Interfaces

Likely future interfaces, in order:

- Python API
- benchmark integration adapter
- optional CLI
- optional service or daemon mode
- optional external tool adapters

Only the Python API is part of the intended early baseline. All other interfaces are deferred until later phases.

## Phase 3A Local Tool Pattern

Recommended Phase 3A pattern: prove one repo-local, read-only tool consumer before adopting larger local clients.

Approved sequencing:

- first controlled local consumer: repo-local CLI utility
- likely second adopter: OpenCode, after the repo-local CLI boundary is proven
- explicitly deferred adopter: OpenClaw, due to higher blast radius and stronger risk of state fragmentation

Recommended dependency direction:

`tools/mlx_control_cli.py -> tools/integrations/mlx_control.py -> mlx_control`

The first Phase 3A surface should stay narrow:

- command surface: `mlx-control status`
- read-only consumption of `MLXController`
- no subprocess behavior
- no runtime/process control
- no service semantics

This keeps the first tool integration repository-local, auditable, and small enough to validate the adapter pattern before larger external-tool adoption.

## Phase 3B OpenCode Pattern

Recommended Phase 3B pattern: adopt OpenCode as the next controlled consumer only through a thin repo-local adapter that composes `mlx_control`.

Approved sequencing:

- next controlled adopter: OpenCode
- explicitly deferred comparison point: OpenClaw

Recommended placement:

- `tools/integrations/opencode_mlx_control.py`

Required dependency direction:

`OpenCode-facing repo glue -> tools/integrations/opencode_mlx_control.py -> mlx_control`

The first Phase 3B slice should stay narrow:

- read-only OpenCode-facing status/readiness adapter
- consume `MLXController`
- no peeking into `mlx_control.state`
- no second local state source
- no provider switching
- no endpoint probing
- no subprocess behavior
- no runtime/process control

This keeps OpenCode adoption aligned with the proven tool boundary without letting a second client redefine control-state ownership.

## Phase 2 Integration Pattern

Recommended pattern: a downstream benchmark adapter layer that composes `mlx_control` from the benchmark side rather than extending `mlx_control` with benchmark concepts.

The benchmark harness should treat `mlx_control` as a control-plane dependency with a small read-oriented interface:

- construct or receive an `MLXController`
- read canonical state through controller methods such as `status()`, `active_model()`, `health()`, and `list_models()`
- translate those benchmark-neutral control views into benchmark decisions, readiness checks, and run-time operator messaging outside `mlx_control`

This keeps the dependency direction one-way:

`benchmark_harness -> benchmark_harness.integrations.mlx_control -> mlx_control`

The integration layer should be thin and repository-local. It is an adapter for benchmark consumption, not a new control-plane home.

## Recommended Adapter Placement

Recommended file and module placement for Phase 2:

- `benchmark_harness/integrations/__init__.py`
- `benchmark_harness/integrations/mlx_control.py`

Why this placement:

- keeps benchmark-specific translation code in the benchmark package
- avoids naming confusion with benchmark model adapters already represented in harness config
- preserves `src/mlx_control/` as benchmark-neutral and extraction-safe
- allows the harness to evolve integration helpers without reshaping the core control module

If multiple benchmark-specific files are eventually needed, they should stay under `benchmark_harness/integrations/mlx_control/` rather than expanding `src/mlx_control/` with benchmark concerns.

## Responsibilities That Stay Inside `mlx_control`

- canonical control-state ownership
- typed control contracts and validation invariants
- benchmark-neutral controller inspection methods
- benchmark-neutral config, registry, state, and health models
- future runtime/process control semantics when that work is explicitly in scope
- invariant enforcement around control-module state transitions

## Responsibilities That Stay Outside `mlx_control`

- benchmark run configuration parsing
- benchmark lane selection, scoring, and escalation policy
- benchmark-specific readiness thresholds and skip rules
- run artifact layout, logging, CSV generation, and summary generation
- benchmark-oriented operator messaging
- repository-local adapter glue that maps benchmark inputs onto `mlx_control` consumption
- any subprocess, shell, or endpoint probing behavior currently owned by the harness

## Anti-Patterns To Avoid

- adding `benchmark_harness` imports anywhere under `src/mlx_control/`
- teaching `mlx_control` about run directories, score files, benchmark task kinds, or benchmark lanes
- reshaping core control contracts around benchmark-only convenience fields
- letting the harness reach into `mlx_control.state` internals when controller methods should be the boundary
- placing benchmark integration code under `src/mlx_control/` just because it is the first consumer
- coupling benchmark integration design to runtime/process control implementation
- introducing subprocess or service management behavior under the banner of Phase 2 integration
- teaching `mlx_control` about CLI presentation concerns for Phase 3A convenience
- letting a first local tool consumer create a second state owner outside `mlx_control`
- jumping to OpenClaw integration before the smaller repo-local CLI boundary is proven
- letting OpenCode-facing code infer readiness from its own local heuristics instead of `MLXController`
- using OpenCode integration as a back door for provider switching or live runtime probing

## Benchmark Separation Rule

Benchmarking is a downstream consumer concern, not the defining architectural center of `mlx_control`.

The benchmark harness may integrate with `mlx_control` no earlier than the scoped work of Phase 2. Until then, the control module should be designed around stable control responsibilities rather than benchmark-specific convenience paths.
