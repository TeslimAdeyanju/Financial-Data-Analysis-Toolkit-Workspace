from __future__ import annotations

from typing import Any, Dict

from fda_toolkit.utils.logging import audit_log
from fda_toolkit.utils.types import optimize_dtypes
from fda_toolkit.utils.security import mask_sensitive_fields, anonymize_identifiers


def get_registry() -> Dict[str, Dict[str, Any]]:
    return {
        "audit_log": {
            "callable": audit_log,
            "category": "Validation, Controls, and Consistency",
            "module": "utils.logging",
            "description": "Create or return an audit log container.",
        },
        "optimize_dtypes": {
            "callable": optimize_dtypes,
            "category": "Performance",
            "module": "utils.types",
            "description": "Downcast dtypes to reduce memory usage.",
        },
        "mask_sensitive_fields": {
            "callable": mask_sensitive_fields,
            "category": "Governance",
            "module": "utils.security",
            "description": "Mask sensitive fields for safe sharing.",
        },
        "anonymize_identifiers": {
            "callable": anonymize_identifiers,
            "category": "Governance",
            "module": "utils.security",
            "description": "Anonymize identifiers using hashing.",
        },
    }
