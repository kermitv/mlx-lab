"""Contract tests for the Phase 1 ``mlx_control`` Python surface."""

from __future__ import annotations

from typing import Tuple

import pytest

from mlx_control import (
    ActiveModelIdentity,
    ControlConfig,
    ControlState,
    DesiredControlMode,
    DesiredState,
    HealthCheck,
    HealthStatus,
    HealthSummary,
    MLXController,
    ModelRegistrySnapshot,
    ModelRegistryState,
    ObservedRuntimeState,
    RuntimePhase,
)


def test_control_state_instantiates_with_explicit_contracts() -> None:
    """The canonical state owner should compose the Phase 1 typed contracts."""

    state = ControlState(
        desired=DesiredState(
            mode=DesiredControlMode.RUNNING,
            target_model_id="mlx-community/Qwen3-8B-4bit",
        ),
        observed=ObservedRuntimeState(
            phase=RuntimePhase.RUNNING,
            active_model_id="mlx-community/Qwen3-8B-4bit",
            detail="runtime observation unavailable in Phase 1",
        ),
        active_model=ActiveModelIdentity(
            model_id="mlx-community/Qwen3-8B-4bit",
            display_name="Qwen3 8B 4-bit",
            revision="main",
        ),
        health=HealthSummary(
            status=HealthStatus.HEALTHY,
            summary="contracts populated",
            checks=(
                HealthCheck(
                    name="state-contract",
                    status=HealthStatus.HEALTHY,
                    detail="typed state instantiated",
                ),
            ),
        ),
        registry=ModelRegistryState(
            models=(
                ModelRegistrySnapshot(
                    model_id="mlx-community/Qwen3-8B-4bit",
                    display_name="Qwen3 8B 4-bit",
                    revision="main",
                    ready=True,
                ),
            ),
        ),
        config=ControlConfig(
            default_model_id="mlx-community/Qwen3-8B-4bit",
            metadata={"owner": "tests"},
        ),
    )

    assert state.desired.mode is DesiredControlMode.RUNNING
    assert state.observed.phase is RuntimePhase.RUNNING
    assert state.active_model is not None
    assert state.active_model.model_id == "mlx-community/Qwen3-8B-4bit"
    assert state.health.status is HealthStatus.HEALTHY
    assert state.registry.get("mlx-community/Qwen3-8B-4bit") is not None
    assert state.config.metadata["owner"] == "tests"


def test_controller_read_surface_returns_canonical_shapes() -> None:
    """Read-only controller methods should return the stored contract types."""

    registry = ModelRegistryState(
        models=(
            ModelRegistrySnapshot(model_id="model-a", ready=True),
            ModelRegistrySnapshot(model_id="model-b", ready=False),
        ),
    )
    state = ControlState(
        active_model=ActiveModelIdentity(model_id="model-a"),
        health=HealthSummary(status=HealthStatus.DEGRADED, summary="placeholder"),
        registry=registry,
    )
    controller = MLXController(state=state)

    assert controller.status() is state
    assert controller.active_model() == ActiveModelIdentity(model_id="model-a")
    assert controller.health() == HealthSummary(
        status=HealthStatus.DEGRADED,
        summary="placeholder",
    )
    assert controller.list_models() == registry.models


@pytest.mark.parametrize(
    ("method_name", "args"),
    [
        ("start", ("model-a",)),
        ("stop", ()),
        ("switch", ("model-b",)),
    ],
)
def test_mutating_controller_methods_are_explicit_stubs(
    method_name: str, args: Tuple[str, ...]
) -> None:
    """Mutation hooks are present but intentionally unimplemented in Phase 1."""

    controller = MLXController(state=ControlState())

    with pytest.raises(NotImplementedError):
        getattr(controller, method_name)(*args)


def test_default_contracts_do_not_imply_runtime_activity() -> None:
    """Default values should remain inert and local-contract oriented."""

    state = ControlState()

    assert state.desired.mode is DesiredControlMode.STOPPED
    assert state.observed.phase is RuntimePhase.UNKNOWN
    assert state.active_model is None
    assert state.registry.models == ()
    assert state.health.status is HealthStatus.UNKNOWN
