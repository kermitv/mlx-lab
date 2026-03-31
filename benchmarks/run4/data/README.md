# Run 4 Data Layer

This directory separates observed benchmark data from derived scoring and presentation fields.

## Files
- `rows.csv`: flat row table for analysis and charting.
- `rows.json`: same data with explicit provenance arrays on each row.
- `routing_summary.json`: derived task-class routing view.

## Provenance
Observed fields come directly from Run 4 benchmark capture artifacts, primarily:
- `benchmark-runs/run-20260329-run4-frontier-boundary/scores/resource_metrics.csv`
- `benchmark-runs/run-20260329-run4-frontier-boundary/scores/quality_scores.csv`
- `benchmark-runs/run-20260329-run4-frontier-boundary/scores/operational_scores.csv`

Derived fields were added after benchmarking to support interpretation and presentation:
- display `model`
- `retries_used`
- `score_structure`
- `score_hallucination_risk`
- `routing_summary.json`

## Important Distinction
It was not fully obvious in the earlier `benchmarks/run4/summary.json` which fields were directly observed versus subsequently derived. This `data/` layer is intended to make that boundary explicit.

## Caveats
- `score_accuracy` and `score_operational` are still benchmark-evaluation outputs rather than raw model outputs.
- `retries_used` is run-level for the model in the source operational table; in Run 4 it only materially affected `gpt-5.4`.
- Local process memory fields remained blocked in Run 4, so `telemetry_ok` should not be read as complete resource observability.
