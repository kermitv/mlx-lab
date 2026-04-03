"""Python-first controller contracts for the internal ``mlx_control`` module.

Phase 1 defines architecture-bearing controller signatures without introducing
runtime, subprocess, service, or benchmark behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from .health import HealthSummary
from .registry import ModelRegistrySnapshot
from .state import ActiveModelIdentity, ControlState


@dataclass
class MLXController:
    """Read-oriented controller facade over canonical control state.

    The controller intentionally exposes inspection methods first. Mutating
    operations remain explicit stubs until a later phase defines runtime
    semantics.
    """

    state: ControlState

    def status(self) -> ControlState:
        """Return the canonical control-visible state snapshot."""

        return self.state

    def active_model(self) -> Optional[ActiveModelIdentity]:
        """Return the canonical active model identity, if one is known."""

        return self.state.active_model

    def health(self) -> HealthSummary:
        """Return the summarized health view from canonical state."""

        return self.state.health

    def list_models(self) -> Tuple[ModelRegistrySnapshot, ...]:
        """Return the registered model inventory visible to the controller."""

        return self.state.registry.models

    def start(self, model_id: str) -> None:
        """Reserved mutation hook for a later runtime-control phase."""

        raise NotImplementedError(
            f"MLXController.start({model_id!r}) is not implemented in Phase 1"
        )

    def stop(self) -> None:
        """Reserved mutation hook for a later runtime-control phase."""

        raise NotImplementedError("MLXController.stop() is not implemented in Phase 1")

    def switch(self, model_id: str) -> None:
        """Reserved mutation hook for a later runtime-control phase."""

        raise NotImplementedError(
            f"MLXController.switch({model_id!r}) is not implemented in Phase 1"
        )
