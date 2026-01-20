from __future__ import annotations

from typing import Any, Dict

from fda_toolkit.validation.schema import standardize_schema, validate_required_fields, validate_category_set
from fda_toolkit.validation.ranges import validate_data_ranges
from fda_toolkit.validation.integrity import (
    assert_primary_key,
    check_referential_integrity,
    check_time_continuity,
    check_data_consistency,
    reconciliation_check,
)
from fda_toolkit.validation.business_rules import validate_business_rules


def get_registry() -> Dict[str, Dict[str, Any]]:
    return {
        "standardize_schema": {
            "callable": standardize_schema,
            "category": "Intake and Structure",
            "module": "validation.schema",
            "description": "Enforce standard schema and required columns.",
        },
        "validate_required_fields": {
            "callable": validate_required_fields,
            "category": "Missing Values and Completeness",
            "module": "validation.schema",
            "description": "Validate required fields.",
        },
        "validate_category_set": {
            "callable": validate_category_set,
            "category": "Categorical Handling and Encoding",
            "module": "validation.schema",
            "description": "Validate values against allowed categories.",
        },
        "validate_data_ranges": {
            "callable": validate_data_ranges,
            "category": "Validation, Controls, and Consistency",
            "module": "validation.ranges",
            "description": "Validate numeric and date ranges.",
        },
        "assert_primary_key": {
            "callable": assert_primary_key,
            "category": "Duplicates and Keys",
            "module": "validation.integrity",
            "description": "Assert primary key uniqueness and non null.",
        },
        "check_referential_integrity": {
            "callable": check_referential_integrity,
            "category": "Validation, Controls, and Consistency",
            "module": "validation.integrity",
            "description": "Check fact to dimension key integrity.",
        },
        "check_time_continuity": {
            "callable": check_time_continuity,
            "category": "Date and Time Feature Engineering",
            "module": "validation.integrity",
            "description": "Check missing dates by frequency.",
        },
        "check_data_consistency": {
            "callable": check_data_consistency,
            "category": "Validation, Controls, and Consistency",
            "module": "validation.integrity",
            "description": "Run cross field consistency checks.",
        },
        "reconciliation_check": {
            "callable": reconciliation_check,
            "category": "Duplicates and Keys",
            "module": "validation.integrity",
            "description": "Compare totals before and after changes.",
        },
        "validate_business_rules": {
            "callable": validate_business_rules,
            "category": "Business Rules",
            "module": "validation.business_rules",
            "description": "Validate custom business rules.",
        },
    }
