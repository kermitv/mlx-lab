"""Tests for benchmark-harness adoption of the MCM preflight adapter."""

from __future__ import annotations

from pathlib import Path

from benchmark_harness.core import BenchmarkConfig, BenchmarkRunner, ModelSpec
from benchmark_harness.integrations.mlx_control import BenchmarkPreflightStatus


class _DummyCallbacks:
    """Small callback stub for runner construction in unit tests."""


def test_evaluate_local_model_preflight_uses_mcm_snapshot_interpretation() -> None:
    """Local model visibility should be interpreted through the MCM adapter."""

    runner = BenchmarkRunner(
        config=BenchmarkConfig(
            run_name="test-run",
            purpose="unit-test preflight adoption",
            execution_mode="test",
            run_dir=Path("/tmp/mlx-lab-preflight-test"),
            local_endpoint="http://127.0.0.1:8080/v1",
            tasks=[],
            models=[],
        ),
        callbacks=_DummyCallbacks(),
    )
    local_specs = [
        ModelSpec(id="model-a", lane="local", adapter="local_chat", required=True),
        ModelSpec(id="model-b", lane="local", adapter="local_chat", required=False),
        ModelSpec(id="missing-model", lane="local", adapter="local_chat", required=True),
    ]

    view, interpretations = runner.evaluate_local_model_preflight(
        local_specs,
        {
            "data": [
                {"id": "model-a"},
                {"id": "model-b"},
            ]
        },
    )

    assert tuple(model.model_id for model in view.registered_models) == (
        "model-a",
        "model-b",
    )
    assert view.is_health_acceptable() is True
    assert interpretations["model-a"].status is BenchmarkPreflightStatus.READY
    assert interpretations["model-a"].requested_model_ready is True
    assert interpretations["model-b"].status is BenchmarkPreflightStatus.READY
    assert interpretations["missing-model"].status is BenchmarkPreflightStatus.NOT_READY
    assert interpretations["missing-model"].requested_model_registered is False
    assert interpretations["missing-model"].requested_model_ready is False
