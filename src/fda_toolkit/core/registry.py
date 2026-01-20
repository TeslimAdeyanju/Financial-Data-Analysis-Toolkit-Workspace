from __future__ import annotations

from typing import Any, Dict

from fda_toolkit.core.columns import clean_column_headers, make_unique_columns
from fda_toolkit.core.missing import coerce_empty_to_nan, fill_missing
from fda_toolkit.core.types import (
    convert_data_types,
    clean_numeric_column,
    clean_boolean_column,
    clean_date_column,
)
from fda_toolkit.core.duplicates import (
    find_duplicates,
    deduplicate_by_priority,
    remove_duplicates,
)
from fda_toolkit.core.text import (
    clean_text_column,
    standardize_text_values,
    clean_categorical_column,
)
from fda_toolkit.core.outliers import (
    detect_outliers_iqr,
    remove_outliers_iqr,
    remove_outliers_zscore,
    flag_outliers,
    cap_outliers,
    winsorize_outliers,
)


def get_registry() -> Dict[str, Dict[str, Any]]:
    return {
        "clean_column_headers": {
            "callable": clean_column_headers,
            "category": "Intake and Structure",
            "module": "core.columns",
            "description": "Standardize column headers.",
        },
        "make_unique_columns": {
            "callable": make_unique_columns,
            "category": "Intake and Structure",
            "module": "core.columns",
            "description": "Ensure column names are unique.",
        },
        "coerce_empty_to_nan": {
            "callable": coerce_empty_to_nan,
            "category": "Intake and Structure",
            "module": "core.missing",
            "description": "Convert empty placeholders to NA.",
        },
        "convert_data_types": {
            "callable": convert_data_types,
            "category": "Data Types and Parsing",
            "module": "core.types",
            "description": "Convert columns to specified dtypes.",
        },
        "clean_numeric_column": {
            "callable": clean_numeric_column,
            "category": "Data Types and Parsing",
            "module": "core.types",
            "description": "Clean numeric strings into numeric dtype.",
        },
        "clean_boolean_column": {
            "callable": clean_boolean_column,
            "category": "Data Types and Parsing",
            "module": "core.types",
            "description": "Standardize boolean like values.",
        },
        "clean_date_column": {
            "callable": clean_date_column,
            "category": "Data Types and Parsing",
            "module": "core.types",
            "description": "Parse date columns safely.",
        },
        "fill_missing": {
            "callable": fill_missing,
            "category": "Missing Values and Completeness",
            "module": "core.missing",
            "description": "Fill missing values with a strategy.",
        },
        "find_duplicates": {
            "callable": find_duplicates,
            "category": "Duplicates and Keys",
            "module": "core.duplicates",
            "description": "Return duplicated rows.",
        },
        "deduplicate_by_priority": {
            "callable": deduplicate_by_priority,
            "category": "Duplicates and Keys",
            "module": "core.duplicates",
            "description": "Deduplicate using a priority rule.",
        },
        "remove_duplicates": {
            "callable": remove_duplicates,
            "category": "Duplicates and Keys",
            "module": "core.duplicates",
            "description": "Remove duplicates.",
        },
        "clean_text_column": {
            "callable": clean_text_column,
            "category": "Text Standardisation",
            "module": "core.text",
            "description": "Clean free text.",
        },
        "standardize_text_values": {
            "callable": standardize_text_values,
            "category": "Text Standardisation",
            "module": "core.text",
            "description": "Standardize text values via mapping.",
        },
        "clean_categorical_column": {
            "callable": clean_categorical_column,
            "category": "Categorical Handling and Encoding",
            "module": "core.text",
            "description": "Clean categorical values.",
        },
        "detect_outliers_iqr": {
            "callable": detect_outliers_iqr,
            "category": "Outliers and Robustness",
            "module": "core.outliers",
            "description": "Detect outliers using IQR.",
        },
        "remove_outliers_iqr": {
            "callable": remove_outliers_iqr,
            "category": "Outliers and Robustness",
            "module": "core.outliers",
            "description": "Remove outliers using IQR.",
        },
        "remove_outliers_zscore": {
            "callable": remove_outliers_zscore,
            "category": "Outliers and Robustness",
            "module": "core.outliers",
            "description": "Remove outliers using z score.",
        },
        "flag_outliers": {
            "callable": flag_outliers,
            "category": "Outliers and Robustness",
            "module": "core.outliers",
            "description": "Flag outliers without dropping rows.",
        },
        "cap_outliers": {
            "callable": cap_outliers,
            "category": "Outliers and Robustness",
            "module": "core.outliers",
            "description": "Cap outliers via quantiles.",
        },
        "winsorize_outliers": {
            "callable": winsorize_outliers,
            "category": "Outliers and Robustness",
            "module": "core.outliers",
            "description": "Winsorize outliers.",
        },
    }
