"""
Schema validation and standardization utilities.

This module provides functions to enforce schema requirements,
validate required fields, and check categorical constraints.
"""

from __future__ import annotations

from typing import Dict, Iterable, Optional

import pandas as pd

from fda_toolkit.utils.logging import audit_log
from fda_toolkit.registry import register_function


@register_function(
    name="standardize_schema",
    category="Validation",
    module="validation.schema",
)
def standardize_schema(
    df: pd.DataFrame,
    required_columns: Iterable[str],
    rename_map: Optional[Dict[str, str]] = None,
    copy: bool = True,
) -> pd.DataFrame:
    """
    Enforce a standard schema.

    Ensures required columns exist and optionally renames columns
    to conform to a standard naming convention.

    Args:
        df (pd.DataFrame): Input DataFrame
        required_columns (Iterable[str]): Column names that must exist
        rename_map (dict): Optional mapping to rename columns. Default: None
        copy (bool): Return a copy or modify in-place. Default: True

    Returns:
        pd.DataFrame: DataFrame with enforced schema

    Raises:
        TypeError: If input is not a DataFrame
        ValueError: If required columns are missing

    Example:
        >>> df = pd.DataFrame({'A': [1], 'B': [2]})
        >>> standardize_schema(df, ['A', 'B'], rename_map={'A': 'col_a'})
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    required = list(required_columns)
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    if copy:
        df = df.copy()

    if rename_map:
        df = df.rename(columns=rename_map)

    audit_log("standardize_schema", before=None, after=df)
    return df


@register_function(
    name="validate_required_fields",
    category="Validation",
    module="validation.schema",
)
def validate_required_fields(
    df: pd.DataFrame,
    required_columns: Iterable[str],
) -> None:
    """
    Raise an error if required columns are missing or fully null.

    Ensures data integrity by validating that all required columns
    exist and contain at least some non-null values.

    Args:
        df (pd.DataFrame): Input DataFrame
        required_columns (Iterable[str]): Columns that must exist and not be empty

    Raises:
        TypeError: If input is not a DataFrame
        ValueError: If any required column is missing or entirely null

    Example:
        >>> df = pd.DataFrame({'id': [1, 2], 'name': [None, None]})
        >>> validate_required_fields(df, ['id', 'name'])
        # Raises: ValueError for 'name' column
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    required = list(required_columns)

    # Check for missing columns
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Required columns missing: {missing}")

    # Check for fully null columns
    fully_null = [col for col in required if df[col].isna().all()]
    if fully_null:
        raise ValueError(f"Required columns are fully null: {fully_null}")

    audit_log("validate_required_fields", before=None, after=None)


@register_function(
    name="validate_category_set",
    category="Validation",
    module="validation.schema",
)
def validate_category_set(
    s: pd.Series,
    allowed: Iterable[str],
    case_insensitive: bool = True,
) -> pd.Series:
    """
    Return a boolean mask for values outside the allowed set.

    Identifies values that violate categorical constraints.

    Args:
        s (pd.Series): Input categorical Series
        allowed (Iterable[str]): Allowed category values
        case_insensitive (bool): Compare case-insensitively. Default: True

    Returns:
        pd.Series: Boolean mask (True = invalid)

    Raises:
        TypeError: If Series is not object/string dtype

    Example:
        >>> s = pd.Series(['A', 'B', 'C', 'D'])
        >>> validate_category_set(s, ['A', 'B']).sum()
        2
    """
    if s.dtype != "object":
        raise TypeError("Series must be object/string dtype")

    s_check = s.copy().astype(str)

    if case_insensitive:
        s_check = s_check.str.lower()
        allowed_set = set(str(v).lower() for v in allowed)
    else:
        allowed_set = set(str(v) for v in allowed)

    invalid = ~s_check.isin(allowed_set)

    audit_log("validate_category_set", before=None, after=invalid)
    return invalid
