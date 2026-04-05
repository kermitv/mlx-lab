# MLX Control Module Decisions

## 2026-04-02

- Internal-first module placement: `mlx_control` begins as an internal repository module under `src/` rather than a separate repository.
- Python-first implementation: the intended primary control surface is Python-first, with CLI and other interfaces deferred.
- Benchmark-to-control dependency direction: benchmark code may consume `mlx_control` later, but `mlx_control` must never depend on `benchmark_harness`.
- Extraction-safe boundary from day one: the package should be shaped for possible extraction later without treating extraction as an immediate deliverable.

## 2026-04-03

- Phase 2 benchmark integration should use a thin downstream adapter layer in `benchmark_harness`, not benchmark-specific extensions inside `mlx_control`.
- Recommended repository-local adapter placement is `benchmark_harness/integrations/mlx_control.py`, with expansion under `benchmark_harness/integrations/mlx_control/` only if multiple benchmark-facing files are later justified.
- `mlx_control` remains responsible for benchmark-neutral control contracts, state, health, registry, and future runtime semantics; benchmark policy, scoring, artifact handling, and run configuration stay outside the module.
- Runtime/process control implementation remains out of scope for the Phase 2 design step and must not be smuggled in through integration work.
- The first concrete Phase 2 adoption slice is a read-only harness preflight path; benchmark execution now consumes the benchmark-side MCM adapter in one real connectivity/preflight workflow.
- Phase 2 closeout does not expand the `mlx_control` public surface for benchmark convenience beyond read-only preflight consumption.
- Phase 3A should start with a repo-local CLI utility as the first controlled local tool consumer of `mlx_control`.
- OpenCode is deferred as a likely second adopter after the repo-local CLI pattern is proven locally.
- OpenClaw is explicitly deferred because it has higher blast radius and greater risk of state fragmentation and accidental runtime coupling.
- Recommended Phase 3A placement is `tools/mlx_control_cli.py` for the entrypoint and `tools/integrations/mlx_control.py` for repo-local adapter glue.
- The first approved Phase 3A command surface is `mlx-control status`.
- Phase 3A remains read-only and must not implement runtime/process control, subprocess behavior, or service semantics.
- Phase 3A closeout establishes the concrete tool boundary `tools -> tools.integrations.mlx_control -> mlx_control` as the first local-tool integration pattern.
- The first concrete Phase 3A implementation includes a repo-local controller-loading path from saved benchmark visibility artifacts rather than live runtime probing.
- The next adopter must be chosen deliberately after Phase 3A rather than folded into the initial CLI slice by convenience.
- Phase 3B selects OpenCode as the next controlled adopter after the repo-local CLI.
- OpenClaw remains explicitly deferred during Phase 3B because its blast radius and coupling risk remain higher than OpenCode.
- Recommended Phase 3B placement is `tools/integrations/opencode_mlx_control.py`.
- The first approved Phase 3B slice is a read-only OpenCode-facing status/readiness adapter.
- Phase 3B remains read-only and must not implement runtime/process control, provider switching, endpoint probing, or subprocess behavior.
- OpenCode-facing code must consume `MLXController` rather than peeking into `mlx_control.state` or inventing a second state source.
- Phase 3B closeout establishes `tools/integrations/opencode_mlx_control.py` as the concrete OpenCode-facing adapter boundary.
- The first concrete Phase 3B adoption slice uses the OpenCode-facing adapter through the existing repo-local `mlx-control status` consumer path.
- OpenCode-facing terminology and readiness logic remain consumer-local concerns and must stay outside `src/mlx_control/`.
