# MLX Control Module Architecture

## Module Boundary

`mlx_control` is the internal control-plane package for MLX lifecycle coordination inside this repository.

In Phase 0, the boundary is documentation and scaffold only. Future runtime work should remain inside `src/mlx_control/` unless there is a clear reason to place repository-specific adapters elsewhere.

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
- `__init__.py`: package marker only in Phase 0

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

## Benchmark Separation Rule

Benchmarking is a downstream consumer concern, not the defining architectural center of `mlx_control`.

The benchmark harness may integrate with `mlx_control` no earlier than the scoped work of Phase 2. Until then, the control module should be designed around stable control responsibilities rather than benchmark-specific convenience paths.
