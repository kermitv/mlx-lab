"""Small exception hierarchy for the internal ``mlx_control`` module."""


class MLXControlError(Exception):
    """Base exception for MCM contract and validation failures."""


class ControlConfigError(MLXControlError):
    """Raised for invalid or inconsistent control configuration."""


class ControlStateError(MLXControlError):
    """Raised for invalid canonical control-state construction or access."""


class ControlHealthError(MLXControlError):
    """Raised for invalid health model construction or access."""
