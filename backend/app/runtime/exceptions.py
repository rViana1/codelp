class WorkspaceNotFoundError(KeyError):
    """Raised when a runtime operation targets an unknown workspace."""


class WorkspaceClosedError(RuntimeError):
    """Raised when a closed workspace is used."""


class InvalidRequestError(ValueError):
    """Raised for a safe, actionable external input failure."""


class CapabilityUnavailableError(RuntimeError):
    """Raised when a requested optional capability is unavailable."""


class InterfaceDisabledError(CapabilityUnavailableError):
    """Raised when configuration disables a requested public interface."""

    def __init__(self, interface: str) -> None:
        super().__init__(f"The {interface} interface is disabled by configuration")
