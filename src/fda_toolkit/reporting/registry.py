from __future__ import annotations

from typing import Any, Dict

from fda_toolkit.reporting.profiling import (
    infer_and_report_types,
    missingness_profile,
    get_data_summary,
    profile_report,
    quick_check,
    memory_profile,
    info,
)
from fda_toolkit.reporting.exceptions import exception_report
from fda_toolkit.reporting.delta import snapshot_dataset, compare_snapshots, delta_report


def get_registry() -> Dict[str, Dict[str, Any]]:
    return {
        "infer_and_report_types": {
            "callable": infer_and_report_types,
            "category": "Data Types and Parsing",
            "module": "reporting.profiling",
            "description": "Report inferred types and dtypes.",
        },
        "missingness_profile": {
            "callable": missingness_profile,
            "category": "Missing Values and Completeness",
            "module": "reporting.profiling",
            "description": "Profile missingness.",
        },
        "get_data_summary": {
            "callable": get_data_summary,
            "category": "Validation, Controls, and Consistency",
            "module": "reporting.profiling",
            "description": "Get dataset summary.",
        },
        "profile_report": {
            "callable": profile_report,
            "category": "Convenience and One Line Utilities",
            "module": "reporting.profiling",
            "description": "Build a combined profile report.",
        },
        "quick_check": {
            "callable": quick_check,
            "category": "Convenience and One Line Utilities",
            "module": "reporting.profiling",
            "description": "Fast diagnostic checks.",
        },
        "memory_profile": {
            "callable": memory_profile,
            "category": "Performance",
            "module": "reporting.profiling",
            "description": "Memory usage by column.",
        },
        "info": {
            "callable": info,
            "category": "Convenience and One Line Utilities",
            "module": "reporting.profiling",
            "description": "Function reference table from registry.",
        },
        "exception_report": {
            "callable": exception_report,
            "category": "Reporting",
            "module": "reporting.exceptions",
            "description": "Create exception report object.",
        },
        "snapshot_dataset": {
            "callable": snapshot_dataset,
            "category": "Reporting",
            "module": "reporting.delta",
            "description": "Create dataset snapshot.",
        },
        "compare_snapshots": {
            "callable": compare_snapshots,
            "category": "Reporting",
            "module": "reporting.delta",
            "description": "Compare dataset snapshots.",
        },
        "delta_report": {
            "callable": delta_report,
            "category": "Reporting",
            "module": "reporting.delta",
            "description": "Report row level deltas.",
        },
    }
