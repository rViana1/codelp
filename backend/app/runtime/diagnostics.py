"""Stable public diagnostic categories shared by every transport."""

from __future__ import annotations

from enum import Enum

from pydantic import ValidationError

from .exceptions import (
    CapabilityUnavailableError,
    InterfaceDisabledError,
    InvalidRequestError,
    WorkspaceClosedError,
    WorkspaceNotFoundError,
)
from .execution import ExecutionConflictError, ExecutionTimeoutError
from .security import WorkspaceSecurityError


class DiagnosticCategory(str, Enum):
    USER = "user_error"
    PROJECT = "project_error"
    CONFIGURATION = "configuration_error"
    CAPABILITY = "capability_unavailable"
    SECURITY = "security_error"
    CONFLICT = "execution_conflict"
    TIMEOUT = "execution_timeout"
    INTERNAL = "internal_error"


def categorize_exception(exc: Exception) -> DiagnosticCategory:
    if isinstance(exc, ValidationError):
        return DiagnosticCategory.CONFIGURATION
    if isinstance(exc, WorkspaceSecurityError):
        return DiagnosticCategory.SECURITY
    if isinstance(exc, ExecutionConflictError):
        return DiagnosticCategory.CONFLICT
    if isinstance(exc, ExecutionTimeoutError):
        return DiagnosticCategory.TIMEOUT
    if isinstance(
        exc,
        (
            FileNotFoundError,
            NotADirectoryError,
            WorkspaceNotFoundError,
            WorkspaceClosedError,
        ),
    ):
        return DiagnosticCategory.PROJECT
    if isinstance(exc, InvalidRequestError):
        return DiagnosticCategory.USER
    if isinstance(exc, CapabilityUnavailableError):
        return DiagnosticCategory.CAPABILITY
    return DiagnosticCategory.INTERNAL


def safe_diagnostic_message(exc: Exception) -> str:
    category = categorize_exception(exc)
    if category == DiagnosticCategory.INTERNAL:
        return "Internal Codelp error; inspect sanitized runtime diagnostics"
    if category == DiagnosticCategory.CONFIGURATION:
        return "Invalid Codelp configuration"
    if category == DiagnosticCategory.TIMEOUT:
        return "Execution is still running after the requested wait timeout"
    if category == DiagnosticCategory.CONFLICT:
        return "A conflicting project execution is already active"
    if isinstance(exc, (InvalidRequestError, InterfaceDisabledError)):
        return str(exc)
    if category == DiagnosticCategory.CAPABILITY:
        return "Requested Codelp capability is unavailable"
    return str(exc).strip("'") or category.value.replace("_", " ")
