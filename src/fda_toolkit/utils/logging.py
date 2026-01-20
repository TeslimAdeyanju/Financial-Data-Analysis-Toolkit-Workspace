"""
Audit logging and tracking utilities.

This module provides data structures and functions to track and record
transformations applied to data for audit and compliance purposes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class AuditEvent:
    """Represents a single audit event."""

    name: str
    timestamp_utc: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditLog:
    """Container for audit events tracking data transformations."""

    events: List[AuditEvent] = field(default_factory=list)

    def add(self, name: str, **details: Any) -> None:
        """
        Add an event to the audit log.

        Args:
            name (str): Event name/operation
            **details: Additional event details as keyword arguments

        Example:
            >>> log = AuditLog()
            >>> log.add("clean_headers", rows=100, columns=10)
        """
        self.events.append(
            AuditEvent(
                name=name,
                timestamp_utc=datetime.utcnow().isoformat(timespec="seconds"),
                details=details,
            )
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert audit log to dictionary format."""
        return {"events": [e.__dict__ for e in self.events]}

    def to_list(self) -> List[Dict[str, Any]]:
        """Convert audit log to list of event dictionaries."""
        return [
            {
                "name": e.name,
                "timestamp_utc": e.timestamp_utc,
                **e.details,
            }
            for e in self.events
        ]

    def __len__(self) -> int:
        """Return number of events in log."""
        return len(self.events)


# Global audit log for tracking function calls
_global_audit_log: Optional[AuditLog] = None


def get_global_audit_log() -> AuditLog:
    """Get or create the global audit log."""
    global _global_audit_log
    if _global_audit_log is None:
        _global_audit_log = AuditLog()
    return _global_audit_log


def reset_audit_log() -> None:
    """Reset the global audit log."""
    global _global_audit_log
    _global_audit_log = None


def audit_log(operation: str, before: Any = None, after: Any = None) -> None:
    """
    Record an operation to the global audit log.

    Intended to be called from within function implementations to track
    data transformations.

    Args:
        operation (str): Name of the operation
        before: State before transformation (optional)
        after: State after transformation (optional)

    Example:
        >>> audit_log("clean_data", before=df.shape, after=clean_df.shape)
    """
    log = get_global_audit_log()

    details = {}
    if before is not None:
        details["before"] = str(before)[:100]  # Truncate long values
    if after is not None:
        details["after"] = str(after)[:100]

    log.add(operation, **details)
