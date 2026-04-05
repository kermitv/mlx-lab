"""OpenCode-facing read-only adapter for consuming ``mlx_control``."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

from mlx_control import HealthStatus, MLXController


class OpenCodeReadinessStatus(str, Enum):
    """Small readiness interpretation for OpenCode local-provider posture."""

    READY = "ready"
    NOT_READY = "not_ready"


@dataclass(frozen=True)
class OpenCodeModelView:
    """OpenCode-facing model inventory entry derived from controller reads."""

    model_id: str
    ready: bool
    display_name: Optional[str] = None
    revision: Optional[str] = None


@dataclass(frozen=True)
class OpenCodeStatusView:
    """Consumer-local OpenCode status/readiness snapshot."""

    active_model_id: Optional[str]
    active_model_display_name: Optional[str]
    active_model_revision: Optional[str]
    health_status: HealthStatus
    health_summary: str
    registered_models: Tuple[OpenCodeModelView, ...]
    ready_models: Tuple[OpenCodeModelView, ...]
    readiness_status: OpenCodeReadinessStatus
    acceptable_for_local_provider: bool


def build_opencode_status_view(controller: MLXController) -> OpenCodeStatusView:
    """Build one OpenCode-facing status/readiness view from controller reads."""

    active_model = controller.active_model()
    health = controller.health()
    registered_models = tuple(
        OpenCodeModelView(
            model_id=model.model_id,
            display_name=model.display_name,
            revision=model.revision,
            ready=model.ready,
        )
        for model in controller.list_models()
    )
    ready_models = tuple(model for model in registered_models if model.ready)
    acceptable_for_local_provider = (
        bool(ready_models)
        and health.status in (HealthStatus.HEALTHY, HealthStatus.DEGRADED)
    )
    readiness_status = (
        OpenCodeReadinessStatus.READY
        if acceptable_for_local_provider
        else OpenCodeReadinessStatus.NOT_READY
    )
    return OpenCodeStatusView(
        active_model_id=active_model.model_id if active_model else None,
        active_model_display_name=active_model.display_name if active_model else None,
        active_model_revision=active_model.revision if active_model else None,
        health_status=health.status,
        health_summary=health.summary,
        registered_models=registered_models,
        ready_models=ready_models,
        readiness_status=readiness_status,
        acceptable_for_local_provider=acceptable_for_local_provider,
    )


def render_opencode_readiness(view: OpenCodeStatusView) -> str:
    """Render one compact OpenCode-facing readiness line."""

    return "OpenCode local-provider readiness: %s" % view.readiness_status.value
