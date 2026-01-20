from __future__ import annotations

from typing import Any, Dict

from fda_toolkit.finance.parsing import parse_currency, parse_percentage, clean_accounting_negative
from fda_toolkit.finance.entities import (
    standardize_entity_names,
    strip_legal_suffixes,
    normalize_reference_codes,
)
from fda_toolkit.finance.rules import (
    impute_by_rule,
    detect_outliers_groupwise,
    seasonality_aware_outliers,
    validate_sign_conventions,
    check_balanced_entries,
)


def get_registry() -> Dict[str, Dict[str, Any]]:
    return {
        "parse_currency": {
            "callable": parse_currency,
            "category": "Data Types and Parsing",
            "module": "finance.parsing",
            "description": "Parse currency strings into numeric values.",
        },
        "parse_percentage": {
            "callable": parse_percentage,
            "category": "Data Types and Parsing",
            "module": "finance.parsing",
            "description": "Parse percentage values into a consistent scale.",
        },
        "clean_accounting_negative": {
            "callable": clean_accounting_negative,
            "category": "Data Types and Parsing",
            "module": "finance.parsing",
            "description": "Convert accounting negatives to negative numbers.",
        },
        "impute_by_rule": {
            "callable": impute_by_rule,
            "category": "Missing Values and Completeness",
            "module": "finance.rules",
            "description": "Impute missing values using explicit rules.",
        },
        "detect_outliers_groupwise": {
            "callable": detect_outliers_groupwise,
            "category": "Outliers and Robustness",
            "module": "finance.rules",
            "description": "Detect outliers within business groups.",
        },
        "seasonality_aware_outliers": {
            "callable": seasonality_aware_outliers,
            "category": "Outliers and Robustness",
            "module": "finance.rules",
            "description": "Detect outliers considering seasonality.",
        },
        "validate_sign_conventions": {
            "callable": validate_sign_conventions,
            "category": "Validation, Controls, and Consistency",
            "module": "finance.rules",
            "description": "Validate sign conventions for columns.",
        },
        "check_balanced_entries": {
            "callable": check_balanced_entries,
            "category": "Validation, Controls, and Consistency",
            "module": "finance.rules",
            "description": "Check debit and credit balance.",
        },
        "standardize_entity_names": {
            "callable": standardize_entity_names,
            "category": "Text Standardisation",
            "module": "finance.entities",
            "description": "Standardize entity names via mapping.",
        },
        "strip_legal_suffixes": {
            "callable": strip_legal_suffixes,
            "category": "Text Standardisation",
            "module": "finance.entities",
            "description": "Strip legal suffixes from entity names.",
        },
        "normalize_reference_codes": {
            "callable": normalize_reference_codes,
            "category": "Text Standardisation",
            "module": "finance.entities",
            "description": "Normalize reference codes such as invoice numbers.",
        },
    }
