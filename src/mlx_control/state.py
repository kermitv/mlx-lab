"""Canonical control-state contracts for the internal ``mlx_control`` module.

This module owns the controller-visible state model for Phase 1. Other modules
may define supporting types, but the aggregate state shape lives here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from .config import ControlConfig
from .health import HealthSummary
from .registry import ModelRegistryState


class DesiredControlMode(str, Enum):
    """Target posture requested by the control module."""

    STOPPED = "stopped"
    RUNNING = "running"


class RuntimePhase(str, Enum):
    """Observed local runtime phase as understood by the control module."""

    UNKNOWN = "unknown"
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass(frozen=True)
class ActiveModelIdentity:
    """Canonical model identity exposed to controller consumers."""

    model_id: str
    display_name: Optional[str] = None
    revision: Optional[str] = None


@dataclass(frozen=True)
class DesiredState:
    """Target control posture requested by higher-level callers."""

    mode: DesiredControlMode = DesiredControlMode.STOPPED
    target_model_id: Optional[str] = None


@dataclass(frozen=True)
class ObservedRuntimeState:
    """Observed local runtime posture without implying control behavior."""

    phase: RuntimePhase = RuntimePhase.UNKNOWN
    active_model_id: Optional[str] = None
    detail: Optional[str] = None


@dataclass(frozen=True)
class ControlState:
    """Single canonical ownership point for controller-visible state."""

    desired: DesiredState = field(default_factory=DesiredState)
    observed: ObservedRuntimeState = field(default_factory=ObservedRuntimeState)
    active_model: Optional[ActiveModelIdentity] = None
    health: HealthSummary = field(default_factory=HealthSummary)
    registry: ModelRegistryState = field(default_factory=ModelRegistryState)
    config: ControlConfig = field(default_factory=ControlConfig)
