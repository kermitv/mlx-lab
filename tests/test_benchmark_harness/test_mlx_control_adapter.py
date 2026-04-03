"""Tests for the read-only benchmark-side ``mlx_control`` adapter."""

from __future__ import annotations

from benchmark_harness.integrations.mlx_control import (
    BenchmarkModelInventoryView,
    BenchmarkPreflightStatus,
    build_preflight_view,
    interpret_controller_preflight,
    interpret_preflight,
    is_expected_model_active,
    is_requested_model_registered,
)
from mlx_control import (
    ControlState,
    HealthCheck,
    HealthStatus,
    HealthSummary,
    MLXController,
    ModelRegistrySnapshot,
    ModelRegistryState,
)


def test_build_preflight_view_translates_controller_reads() -> None:
    """The adapter should expose a small benchmark-facing snapshot."""

    controller = MLXController(
        state=ControlState.running(
            "model-a",
            display_name="Model A",
            revision="main",
            health=HealthSummary(
                status=HealthStatus.HEALTHY,
                summary="ready for inspection",
                checks=(
                    HealthCheck(
                        name="registry",
                        status=HealthStatus.HEALTHY,
                        detail="inventory loaded",
                    ),
                ),
            ),
            registry=ModelRegistryState(
                models=(
                    ModelRegistrySnapshot(
                        model_id="model-a",
                        display_name="Model A",
                        revision="main",
                        ready=True,
                    ),
                    ModelRegistrySnapshot(
                        model_id="model-b",
                        display_name="Model B",
                        revision="staged",
                        ready=False,
                    ),
                ),
            ),
        )
    )

    view = build_preflight_view(controller)

    assert view.active_model_id == "model-a"
    assert view.active_model_display_name == "Model A"
    assert view.active_model_revision == "main"
    assert view.health_status is HealthStatus.HEALTHY
    assert view.health_summary == "ready for inspection"
    assert view.registered_models == (
        BenchmarkModelInventoryView(
            model_id="model-a",
            display_name="Model A",
            revision="main",
            ready=True,
        ),
        BenchmarkModelInventoryView(
            model_id="model-b",
            display_name="Model B",
            revision="staged",
            ready=False,
        ),
    )


def test_build_preflight_view_handles_inert_controller_state() -> None:
    """Missing active model data should remain explicit in benchmark reads."""

    controller = MLXController(
        state=ControlState.stopped(
            health=HealthSummary(
                status=HealthStatus.UNKNOWN,
                summary="runtime not implemented",
            ),
            registry=ModelRegistryState(
                models=(ModelRegistrySnapshot(model_id="model-a", ready=True),),
            ),
        )
    )

    view = build_preflight_view(controller)

    assert view.active_model_id is None
    assert view.active_model_display_name is None
    assert view.active_model_revision is None
    assert view.health_status is HealthStatus.UNKNOWN
    assert view.is_expected_model_active("model-a") is False
    assert view.is_requested_model_registered("model-a") is True
    assert view.is_requested_model_ready("model-a") is True
    assert view.has_any_ready_models() is True
    assert view.is_health_acceptable() is False


def test_expected_model_active_helper_uses_controller_read_boundary() -> None:
    """Expected-model checks should be available without state peeking."""

    controller = MLXController(
        state=ControlState.running(
            "model-a",
            health=HealthSummary(
                status=HealthStatus.DEGRADED,
                summary="placeholder",
            ),
            registry=ModelRegistryState(
                models=(ModelRegistrySnapshot(model_id="model-a", ready=True),),
            ),
        ),
    )

    assert is_expected_model_active(controller, "model-a") is True
    assert is_expected_model_active(controller, "model-b") is False


def test_requested_model_registered_helper_checks_inventory_presence() -> None:
    """Inventory checks should stay bound to controller-visible registry reads."""

    controller = MLXController(
        state=ControlState.running(
            "model-a",
            health=HealthSummary(
                status=HealthStatus.DEGRADED,
                summary="placeholder",
            ),
            registry=ModelRegistryState(
                models=(
                    ModelRegistrySnapshot(model_id="model-a", ready=True),
                    ModelRegistrySnapshot(model_id="model-b", ready=False),
                ),
            ),
        ),
    )

    assert is_requested_model_registered(controller, "model-b") is True
    assert is_requested_model_registered(controller, "missing-model") is False


def test_preflight_view_reports_ready_inventory_and_requested_readiness() -> None:
    """Snapshot helpers should expose ready-model checks without controller peeking."""

    controller = MLXController(
        state=ControlState.running(
            "model-a",
            health=HealthSummary(
                status=HealthStatus.HEALTHY,
                summary="ready",
            ),
            registry=ModelRegistryState(
                models=(
                    ModelRegistrySnapshot(model_id="model-a", ready=True),
                    ModelRegistrySnapshot(model_id="model-b", ready=False),
                ),
            ),
        ),
    )

    view = build_preflight_view(controller)

    assert view.ready_models() == (BenchmarkModelInventoryView(model_id="model-a", ready=True),)
    assert view.has_any_ready_models() is True
    assert view.is_requested_model_ready("model-a") is True
    assert view.is_requested_model_ready("model-b") is False


def test_interpret_preflight_returns_ready_for_minimal_acceptable_snapshot() -> None:
    """A healthy or degraded ready snapshot should pass minimal preflight."""

    view = build_preflight_view(
        MLXController(
            state=ControlState.running(
                "model-a",
                health=HealthSummary(
                    status=HealthStatus.DEGRADED,
                    summary="acceptable for read-only benchmark start",
                ),
                registry=ModelRegistryState(
                    models=(
                        ModelRegistrySnapshot(model_id="model-a", ready=True),
                        ModelRegistrySnapshot(model_id="model-b", ready=False),
                    ),
                ),
            ),
        )
    )

    interpretation = interpret_preflight(
        view,
        requested_model_id="model-a",
        expected_active_model_id="model-a",
    )

    assert interpretation.status is BenchmarkPreflightStatus.READY
    assert interpretation.active_model_matches_expected is True
    assert interpretation.requested_model_registered is True
    assert interpretation.requested_model_ready is True
    assert interpretation.has_any_ready_models is True
    assert interpretation.health_acceptable is True
    assert interpretation.can_start_benchmark is True


def test_interpret_preflight_rejects_unready_requested_model() -> None:
    """Requested-model readiness should block a preflight pass when absent or unready."""

    view = build_preflight_view(
        MLXController(
            state=ControlState.running(
                "model-a",
                health=HealthSummary(
                    status=HealthStatus.HEALTHY,
                    summary="inventory available",
                ),
                registry=ModelRegistryState(
                    models=(
                        ModelRegistrySnapshot(model_id="model-a", ready=True),
                        ModelRegistrySnapshot(model_id="model-b", ready=False),
                    ),
                ),
            ),
        )
    )

    interpretation = interpret_preflight(
        view,
        requested_model_id="model-b",
        expected_active_model_id="model-a",
    )

    assert interpretation.status is BenchmarkPreflightStatus.NOT_READY
    assert interpretation.active_model_matches_expected is True
    assert interpretation.requested_model_registered is True
    assert interpretation.requested_model_ready is False
    assert interpretation.has_any_ready_models is True
    assert interpretation.health_acceptable is True
    assert interpretation.can_start_benchmark is False


def test_interpret_controller_preflight_uses_single_snapshot_boundary() -> None:
    """Controller interpretation should compose build-plus-interpret in one call."""

    controller = MLXController(
        state=ControlState.stopped(
            health=HealthSummary(
                status=HealthStatus.UNHEALTHY,
                summary="not acceptable",
            ),
            registry=ModelRegistryState(
                models=(ModelRegistrySnapshot(model_id="model-a", ready=False),),
            ),
        )
    )

    interpretation = interpret_controller_preflight(
        controller,
        requested_model_id="model-a",
        expected_active_model_id="model-a",
    )

    assert interpretation.status is BenchmarkPreflightStatus.NOT_READY
    assert interpretation.active_model_matches_expected is False
    assert interpretation.requested_model_registered is True
    assert interpretation.requested_model_ready is False
    assert interpretation.has_any_ready_models is False
    assert interpretation.health_acceptable is False
