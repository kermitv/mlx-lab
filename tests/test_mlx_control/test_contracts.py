"""Contract tests for the Phase 1 ``mlx_control`` Python surface."""

from __future__ import annotations

from typing import Tuple

import pytest

from mlx_control import (
    ActiveModelIdentity,
    ControlConfig,
    ControlConfigError,
    ControlState,
    ControlStateError,
    DesiredControlMode,
    DesiredState,
    HealthCheck,
    ControlHealthError,
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


def test_ergonomic_constructors_build_stopped_state() -> None:
    """Stopped helpers should build an inert valid canonical snapshot."""

    state = ControlState.stopped()

    assert state.desired == DesiredState.stopped()
    assert state.observed == ObservedRuntimeState.stopped()
    assert state.is_running is False
    assert state.is_transitioning is False
    assert state.has_active_model is False


def test_ergonomic_constructors_build_running_state() -> None:
    """Running helpers should build a valid steady-state snapshot."""

    state = ControlState.running(
        "model-a",
        display_name="Model A",
        revision="main",
        detail="steady",
    )

    assert state.desired == DesiredState.running("model-a")
    assert state.observed == ObservedRuntimeState.running("model-a", detail="steady")
    assert state.active_model == ActiveModelIdentity(
        model_id="model-a",
        display_name="Model A",
        revision="main",
    )
    assert state.is_running is True
    assert state.is_transitioning is False
    assert state.has_active_model is True


def test_observed_runtime_helpers_cover_transition_phases() -> None:
    """Observed runtime helpers should provide valid common phase shapes."""

    starting = ObservedRuntimeState.starting("model-a", detail="booting")
    stopping = ObservedRuntimeState.stopping("model-a", detail="draining")

    assert starting.phase is RuntimePhase.STARTING
    assert starting.active_model_id == "model-a"
    assert starting.is_transitioning is True
    assert stopping.phase is RuntimePhase.STOPPING
    assert stopping.active_model_id == "model-a"
    assert stopping.is_transitioning is True


def test_registry_convenience_helpers_return_filtered_views() -> None:
    """Registry convenience helpers should improve read-only consumption."""

    registry = ModelRegistryState(
        models=(
            ModelRegistrySnapshot(model_id="model-a", ready=True),
            ModelRegistrySnapshot(model_id="model-b", ready=False),
        )
    )

    assert registry.model_ids == ("model-a", "model-b")
    assert registry.contains("model-a") is True
    assert registry.contains("missing-model") is False
    assert registry.ready_models() == (ModelRegistrySnapshot(model_id="model-a", ready=True),)


def test_running_desired_state_requires_target_model_id() -> None:
    """A running target posture must name the intended model."""

    with pytest.raises(ControlStateError):
        DesiredState(mode=DesiredControlMode.RUNNING)


def test_stopped_desired_state_rejects_target_model_id() -> None:
    """Stopped desired posture should not imply an active target model."""

    with pytest.raises(ControlStateError):
        DesiredState(
            mode=DesiredControlMode.STOPPED,
            target_model_id="model-a",
        )


def test_observed_stopped_state_rejects_active_model_id() -> None:
    """Stopped or unknown observations should not report an active runtime id."""

    with pytest.raises(ControlStateError):
        ObservedRuntimeState(
            phase=RuntimePhase.STOPPED,
            active_model_id="model-a",
        )


def test_running_observation_requires_canonical_active_model_alignment() -> None:
    """Running state requires canonical and observed active identities to agree."""

    with pytest.raises(ControlStateError):
        ControlState(
            desired=DesiredState(
                mode=DesiredControlMode.RUNNING,
                target_model_id="model-a",
            ),
            observed=ObservedRuntimeState(
                phase=RuntimePhase.RUNNING,
                active_model_id="model-a",
            ),
        )

    with pytest.raises(ControlStateError):
        ControlState(
            desired=DesiredState(
                mode=DesiredControlMode.RUNNING,
                target_model_id="model-a",
            ),
            observed=ObservedRuntimeState(
                phase=RuntimePhase.RUNNING,
                active_model_id="model-b",
            ),
            active_model=ActiveModelIdentity(model_id="model-a"),
        )


def test_running_state_allows_transitional_divergence_outside_running_phase() -> None:
    """Observed runtime data may diverge from canonical identity during transitions."""

    state = ControlState(
        desired=DesiredState(
            mode=DesiredControlMode.RUNNING,
            target_model_id="model-a",
        ),
        observed=ObservedRuntimeState(
            phase=RuntimePhase.STARTING,
            active_model_id="model-b",
        ),
        active_model=ActiveModelIdentity(model_id="model-a"),
    )

    assert state.active_model.model_id == "model-a"
    assert state.observed.active_model_id == "model-b"


def test_running_state_requires_desired_and_canonical_alignment() -> None:
    """Steady running state should not split desired and canonical identities."""

    with pytest.raises(ControlStateError):
        ControlState(
            desired=DesiredState(
                mode=DesiredControlMode.RUNNING,
                target_model_id="model-a",
            ),
            observed=ObservedRuntimeState(
                phase=RuntimePhase.RUNNING,
                active_model_id="model-b",
            ),
            active_model=ActiveModelIdentity(model_id="model-b"),
        )


def test_config_validation_rejects_blank_values() -> None:
    """Configuration validation should reject blank identifiers and metadata."""

    with pytest.raises(ControlConfigError):
        ControlConfig(default_model_id="  ")

    with pytest.raises(ControlConfigError):
        ControlConfig(metadata={"": "value"})

    with pytest.raises(ControlConfigError):
        ControlConfig(metadata={"owner": " "})


def test_health_validation_rejects_inconsistent_summary() -> None:
    """Health summaries should not claim healthy while containing bad checks."""

    with pytest.raises(ControlHealthError):
        HealthCheck(name="  ", status=HealthStatus.HEALTHY)

    with pytest.raises(ControlHealthError):
        HealthSummary(
            status=HealthStatus.HEALTHY,
            summary="healthy",
            checks=(
                HealthCheck(
                    name="runtime",
                    status=HealthStatus.DEGRADED,
                ),
            ),
        )
