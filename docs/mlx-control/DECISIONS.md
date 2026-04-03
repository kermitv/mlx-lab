# MLX Control Module Decisions

## 2026-04-02

- Internal-first module placement: `mlx_control` begins as an internal repository module under `src/` rather than a separate repository.
- Python-first implementation: the intended primary control surface is Python-first, with CLI and other interfaces deferred.
- Benchmark-to-control dependency direction: benchmark code may consume `mlx_control` later, but `mlx_control` must never depend on `benchmark_harness`.
- Extraction-safe boundary from day one: the package should be shaped for possible extraction later without treating extraction as an immediate deliverable.
