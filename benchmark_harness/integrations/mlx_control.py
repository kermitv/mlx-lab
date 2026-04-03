"""Read-only benchmark adapter for consuming ``mlx_control`` contracts.

This module intentionally stays thin. It translates the benchmark-neutral
``MLXController`` read surface into benchmark-facing helper views without
introducing runtime control, subprocess behavior, or benchmark policy.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

from mlx_control import HealthStatus, MLXController


@dataclass(frozen=True)
class BenchmarkModelInventoryView:
    """Benchmark-facing read model for a registered inventory entry."""

    model_id: str
    display_name: Optional[str] = None
    revision: Optional[str] = None
    ready: bool = False


@dataclass(frozen=True)
class BenchmarkPreflightView:
    """Small benchmark-side snapshot derived from ``MLXController`` reads."""

    active_model_id: Optional[str]
    active_model_display_name: Optional[str]
    active_model_revision: Optional[str]
    health_status: HealthStatus
    health_summary: str
    registered_models: Tuple[BenchmarkModelInventoryView, ...]

    def is_expected_model_active(self, model_id: str) -> bool:
        """Return whether the expected model is the canonical active model."""

        return self.active_model_id == model_id

    def is_requested_model_registered(self, model_id: str) -> bool:
        """Return whether the requested model exists in the visible inventory."""

        return any(model.model_id == model_id for model in self.registered_models)

    def ready_models(self) -> Tuple[BenchmarkModelInventoryView, ...]:
        """Return the registered models currently marked ready."""

        return tuple(model for model in self.registered_models if model.ready)

    def has_any_ready_models(self) -> bool:
        """Return whether any registered model is currently marked ready."""

        return any(model.ready for model in self.registered_models)

    def is_requested_model_ready(self, model_id: str) -> bool:
        """Return whether the requested model exists and is marked ready."""

        return any(
            model.model_id == model_id and model.ready
            for model in self.registered_models
        )

    def is_health_acceptable(self) -> bool:
        """Return whether health is acceptable for a benchmark preflight pass."""

        return self.health_status in (HealthStatus.HEALTHY, HealthStatus.DEGRADED)


class BenchmarkPreflightStatus(str, Enum):
    """Small benchmark-side readiness status derived from one snapshot."""

    READY = "ready"
    NOT_READY = "not_ready"


@dataclass(frozen=True)
class BenchmarkPreflightInterpretation:
    """Read-only benchmark interpretation derived from one preflight snapshot."""

    status: BenchmarkPreflightStatus
    active_model_matches_expected: bool
    requested_model_registered: bool
    requested_model_ready: bool
    has_any_ready_models: bool
    health_acceptable: bool

    @property
    def can_start_benchmark(self) -> bool:
        """Return whether the snapshot meets the minimal benchmark start posture."""

        return self.status is BenchmarkPreflightStatus.READY


def build_preflight_view(controller: MLXController) -> BenchmarkPreflightView:
    """Build a benchmark-side read snapshot from the controller boundary."""

    active_model = controller.active_model()
    health = controller.health()
    registered_models = tuple(
        BenchmarkModelInventoryView(
            model_id=model.model_id,
            display_name=model.display_name,
            revision=model.revision,
            ready=model.ready,
        )
        for model in controller.list_models()
    )
    return BenchmarkPreflightView(
        active_model_id=active_model.model_id if active_model else None,
        active_model_display_name=active_model.display_name if active_model else None,
        active_model_revision=active_model.revision if active_model else None,
        health_status=health.status,
        health_summary=health.summary,
        registered_models=registered_models,
    )


def is_expected_model_active(controller: MLXController, model_id: str) -> bool:
    """Return whether a specific model is currently active."""

    return build_preflight_view(controller).is_expected_model_active(model_id)


def is_requested_model_registered(controller: MLXController, model_id: str) -> bool:
    """Return whether a specific model is present in controller-visible inventory."""

    return build_preflight_view(controller).is_requested_model_registered(model_id)


def interpret_preflight(
    view: BenchmarkPreflightView,
    *,
    requested_model_id: Optional[str] = None,
    expected_active_model_id: Optional[str] = None,
) -> BenchmarkPreflightInterpretation:
    """Interpret one preflight snapshot into minimal benchmark readiness signals."""

    active_model_matches_expected = (
        True
        if expected_active_model_id is None
        else view.is_expected_model_active(expected_active_model_id)
    )
    requested_model_registered = (
        True
        if requested_model_id is None
        else view.is_requested_model_registered(requested_model_id)
    )
    requested_model_ready = (
        True
        if requested_model_id is None
        else view.is_requested_model_ready(requested_model_id)
    )
    has_any_ready_models = view.has_any_ready_models()
    health_acceptable = view.is_health_acceptable()
    status = (
        BenchmarkPreflightStatus.READY
        if (
            active_model_matches_expected
            and requested_model_registered
            and requested_model_ready
            and has_any_ready_models
            and health_acceptable
        )
        else BenchmarkPreflightStatus.NOT_READY
    )
    return BenchmarkPreflightInterpretation(
        status=status,
        active_model_matches_expected=active_model_matches_expected,
        requested_model_registered=requested_model_registered,
        requested_model_ready=requested_model_ready,
        has_any_ready_models=has_any_ready_models,
        health_acceptable=health_acceptable,
    )


def interpret_controller_preflight(
    controller: MLXController,
    *,
    requested_model_id: Optional[str] = None,
    expected_active_model_id: Optional[str] = None,
) -> BenchmarkPreflightInterpretation:
    """Build and interpret one preflight snapshot from the controller boundary."""

    return interpret_preflight(
        build_preflight_view(controller),
        requested_model_id=requested_model_id,
        expected_active_model_id=expected_active_model_id,
    )
