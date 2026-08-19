class WorkspaceNotFoundError(KeyError):
    """Raised when a runtime operation targets an unknown workspace."""


class WorkspaceClosedError(RuntimeError):
    """Raised when a closed workspace is used."""
