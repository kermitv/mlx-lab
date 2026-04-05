"""Tests for the Phase 3B OpenCode-facing ``mlx_control`` adapter."""

from __future__ import annotations

from mlx_control import (
    ControlState,
    HealthStatus,
    HealthSummary,
    MLXController,
    ModelRegistrySnapshot,
    ModelRegistryState,
)
from tools.integrations.opencode_mlx_control import (
    OpenCodeModelView,
    OpenCodeReadinessStatus,
    build_opencode_status_view,
    render_opencode_readiness,
)


def test_build_opencode_status_view_uses_controller_reads_only() -> None:
    """The OpenCode adapter should derive its view from controller methods."""

    controller = MLXController(
        state=ControlState.running(
            "model-a",
            display_name="Model A",
            revision="main",
            health=HealthSummary(
                status=HealthStatus.HEALTHY,
                summary="ready for local provider use",
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

    view = build_opencode_status_view(controller)

    assert view.active_model_id == "model-a"
    assert view.active_model_display_name == "Model A"
    assert view.active_model_revision == "main"
    assert view.health_status is HealthStatus.HEALTHY
    assert view.health_summary == "ready for local provider use"
    assert view.registered_models == (
        OpenCodeModelView(
            model_id="model-a",
            display_name="Model A",
            revision="main",
            ready=True,
        ),
        OpenCodeModelView(
            model_id="model-b",
            display_name="Model B",
            revision="staged",
            ready=False,
        ),
    )
    assert view.ready_models == (
        OpenCodeModelView(
            model_id="model-a",
            display_name="Model A",
            revision="main",
            ready=True,
        ),
    )
    assert view.readiness_status is OpenCodeReadinessStatus.READY
    assert view.acceptable_for_local_provider is True


def test_build_opencode_status_view_accepts_degraded_when_ready_models_exist() -> None:
    """Degraded health can remain acceptable for local-provider posture."""

    controller = MLXController(
        state=ControlState.stopped(
            health=HealthSummary(
                status=HealthStatus.DEGRADED,
                summary="read-only degraded placeholder",
            ),
            registry=ModelRegistryState(
                models=(ModelRegistrySnapshot(model_id="model-a", ready=True),),
            ),
        )
    )

    view = build_opencode_status_view(controller)

    assert view.health_status is HealthStatus.DEGRADED
    assert tuple(model.model_id for model in view.ready_models) == ("model-a",)
    assert view.readiness_status is OpenCodeReadinessStatus.READY
    assert view.acceptable_for_local_provider is True


def test_build_opencode_status_view_rejects_missing_ready_models() -> None:
    """OpenCode readiness should fail when no ready models are visible."""

    controller = MLXController(
        state=ControlState.stopped(
            health=HealthSummary(
                status=HealthStatus.HEALTHY,
                summary="inventory loaded",
            ),
            registry=ModelRegistryState(
                models=(
                    ModelRegistrySnapshot(model_id="model-a", ready=False),
                    ModelRegistrySnapshot(model_id="model-b", ready=False),
                ),
            ),
        )
    )

    view = build_opencode_status_view(controller)

    assert view.ready_models == ()
    assert view.readiness_status is OpenCodeReadinessStatus.NOT_READY
    assert view.acceptable_for_local_provider is False


def test_build_opencode_status_view_rejects_unhealthy_or_unknown_health() -> None:
    """OpenCode readiness should remain blocked when health is not acceptable."""

    unhealthy = build_opencode_status_view(
        MLXController(
            state=ControlState.stopped(
                health=HealthSummary(
                    status=HealthStatus.UNHEALTHY,
                    summary="not suitable",
                ),
                registry=ModelRegistryState(
                    models=(ModelRegistrySnapshot(model_id="model-a", ready=True),),
                ),
            )
        )
    )
    unknown = build_opencode_status_view(
        MLXController(
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
    )

    assert unhealthy.readiness_status is OpenCodeReadinessStatus.NOT_READY
    assert unhealthy.acceptable_for_local_provider is False
    assert unknown.readiness_status is OpenCodeReadinessStatus.NOT_READY
    assert unknown.acceptable_for_local_provider is False


def test_render_opencode_readiness_returns_compact_consumer_line() -> None:
    """Rendered readiness should stay compact for repo-local consumer output."""

    ready_line = render_opencode_readiness(
        build_opencode_status_view(
            MLXController(
                state=ControlState.stopped(
                    health=HealthSummary(
                        status=HealthStatus.DEGRADED,
                        summary="acceptable",
                    ),
                    registry=ModelRegistryState(
                        models=(ModelRegistrySnapshot(model_id="model-a", ready=True),),
                    ),
                )
            )
        )
    )
    blocked_line = render_opencode_readiness(
        build_opencode_status_view(
            MLXController(
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
        )
    )

    assert ready_line == "OpenCode local-provider readiness: ready"
    assert blocked_line == "OpenCode local-provider readiness: not_ready"
