"""
Data integrity validation utilities.

This module provides functions to validate primary keys, referential integrity,
time continuity, and data consistency.
"""

from __future__ import annotations

from typing import Iterable, Optional

import pandas as pd

from fda_toolkit.utils.logging import audit_log
from fda_toolkit.registry import register_function


@register_function(
    name="assert_primary_key",
    category="Validation",
    module="validation.integrity",
)
def assert_primary_key(
    df: pd.DataFrame,
    key_cols: Iterable[str],
) -> None:
    """
    Raise if primary key is null or duplicated.

    Validates that specified columns form a unique, non-null primary key.

    Args:
        df (pd.DataFrame): Input DataFrame
        key_cols (Iterable[str]): Column(s) forming the primary key

    Raises:
        TypeError: If input is not a DataFrame
        ValueError: If primary key contains nulls or duplicates

    Example:
        >>> df = pd.DataFrame({'id': [1, 2, 3], 'name': ['a', 'b', 'c']})
        >>> assert_primary_key(df, ['id'])  # OK
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    key_cols = list(key_cols)

    # Check for missing columns
    missing = [col for col in key_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Columns not found: {missing}")

    # Check for nulls in key
    null_in_key = df[key_cols].isna().any(axis=1).sum()
    if null_in_key > 0:
        raise ValueError(f"Primary key contains {null_in_key} null value(s)")

    # Check for duplicates
    duplicates = df.duplicated(subset=key_cols).sum()
    if duplicates > 0:
        raise ValueError(f"Primary key has {duplicates} duplicate(s)")

    audit_log("assert_primary_key", before=None, after=None)


@register_function(
    name="check_referential_integrity",
    category="Validation",
    module="validation.integrity",
)
def check_referential_integrity(
    fact: pd.DataFrame,
    dim: pd.DataFrame,
    fact_key: str,
    dim_key: str,
) -> pd.DataFrame:
    """
    Return fact rows with missing dimension keys.

    Validates that all foreign keys in the fact table exist in the dimension.

    Args:
        fact (pd.DataFrame): Fact table
        dim (pd.DataFrame): Dimension table
        fact_key (str): Foreign key column in fact table
        dim_key (str): Primary key column in dimension table

    Returns:
        pd.DataFrame: Fact rows with missing references

    Raises:
        TypeError: If tables are not DataFrames
        ValueError: If columns don't exist

    Example:
        >>> fact = pd.DataFrame({'product_id': [1, 2, 3, 99]})
        >>> dim = pd.DataFrame({'id': [1, 2, 3]})
        >>> orphans = check_referential_integrity(fact, dim, 'product_id', 'id')
        >>> len(orphans)
        1
    """
    if not isinstance(fact, pd.DataFrame) or not isinstance(dim, pd.DataFrame):
        raise TypeError("Both fact and dim must be DataFrames")

    if fact_key not in fact.columns:
        raise ValueError(f"Column '{fact_key}' not found in fact table")
    if dim_key not in dim.columns:
        raise ValueError(f"Column '{dim_key}' not found in dim table")

    valid_keys = set(dim[dim_key].dropna())
    orphans = fact[~fact[fact_key].isin(valid_keys)]

    audit_log("check_referential_integrity", before=None, after=orphans)
    return orphans


@register_function(
    name="check_time_continuity",
    category="Validation",
    module="validation.integrity",
)
def check_time_continuity(
    df: pd.DataFrame,
    date_col: str,
    freq: str = "D",
) -> pd.DataFrame:
    """
    Return missing dates based on a frequency.

    Identifies gaps in date sequences for time-series validation.

    Args:
        df (pd.DataFrame): Input DataFrame
        date_col (str): Date column name
        freq (str): Frequency code - 'D' (day), 'W' (week), 'M' (month). Default: 'D'

    Returns:
        pd.DataFrame: Expected dates that are missing from the data

    Raises:
        TypeError: If input is not a DataFrame
        ValueError: If date_col doesn't exist or isn't datetime

    Example:
        >>> df = pd.DataFrame({
        ...     'date': pd.to_datetime(['2020-01-01', '2020-01-03', '2020-01-05'])
        ... })
        >>> missing = check_time_continuity(df, 'date', 'D')
        >>> len(missing)
        2
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    if date_col not in df.columns:
        raise ValueError(f"Column '{date_col}' not found")

    if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
        raise ValueError(f"Column '{date_col}' is not datetime type")

    dates = pd.to_datetime(df[date_col]).dropna().sort_values()

    if len(dates) < 2:
        return pd.DataFrame()

    expected_dates = pd.date_range(start=dates.min(), end=dates.max(), freq=freq)
    actual_dates = set(dates)

    missing = pd.DataFrame(
        {date_col: [d for d in expected_dates if d not in actual_dates]}
    )

    audit_log("check_time_continuity", before=None, after=missing)
    return missing


@register_function(
    name="check_data_consistency",
    category="Validation",
    module="validation.integrity",
)
def check_data_consistency(df: pd.DataFrame) -> pd.DataFrame:
    """
    Run consistency checks and return issues.

    Performs general data quality checks for common inconsistencies.

    Args:
        df (pd.DataFrame): Input DataFrame

    Returns:
        pd.DataFrame: Summary report of consistency issues

    Raises:
        TypeError: If input is not a DataFrame

    Example:
        >>> df = pd.DataFrame({'A': [1, 'text', 3]})
        >>> issues = check_data_consistency(df)
        >>> issues[issues['column'] == 'A']
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    issues = []

    for col in df.columns:
        # Check for high null percentage
        null_pct = df[col].isna().sum() / len(df) * 100
        if null_pct > 50:
            issues.append(
                {"column": col, "issue": "high_null", "percentage": null_pct}
            )

        # Check for constant values (single unique value)
        if df[col].nunique() == 1:
            issues.append({"column": col, "issue": "constant_values", "value": df[col].iloc[0]})

        # Check for suspicious types in numeric columns
        if pd.api.types.is_numeric_dtype(df[col]):
            if (df[col] == 0).sum() > len(df) * 0.9:
                issues.append(
                    {"column": col, "issue": "mostly_zeros", "percentage": 90}
                )

    result = pd.DataFrame(issues) if issues else pd.DataFrame()

    audit_log("check_data_consistency", before=None, after=result)
    return result


@register_function(
    name="reconciliation_check",
    category="Validation",
    module="validation.integrity",
)
def reconciliation_check(
    before: pd.DataFrame,
    after: pd.DataFrame,
    value_cols: Iterable[str],
    group_cols: Optional[Iterable[str]] = None,
) -> pd.DataFrame:
    """
    Compare totals before and after a transformation.

    Validates data quality by ensuring that aggregated values are
    preserved through transformations.

    Args:
        before (pd.DataFrame): Data before transformation
        after (pd.DataFrame): Data after transformation
        value_cols (Iterable[str]): Columns to reconcile
        group_cols (Iterable[str]): Columns to group by. Default: None (overall total)

    Returns:
        pd.DataFrame: Reconciliation report with before, after, and delta

    Raises:
        TypeError: If inputs are not DataFrames
        ValueError: If columns don't exist

    Example:
        >>> before = pd.DataFrame({'type': ['A', 'A', 'B'], 'amount': [10, 20, 30]})
        >>> after = pd.DataFrame({'type': ['A', 'B'], 'amount': [30, 30]})
        >>> reconciliation_check(before, after, ['amount'], ['type'])
    """
    if not isinstance(before, pd.DataFrame) or not isinstance(after, pd.DataFrame):
        raise TypeError("Both before and after must be DataFrames")

    value_cols = list(value_cols)

    if group_cols is None:
        # Overall totals
        before_totals = before[value_cols].sum()
        after_totals = after[value_cols].sum()

        result = pd.DataFrame(
            {
                "column": value_cols,
                "before": before_totals.values,
                "after": after_totals.values,
            }
        )
        result["delta"] = result["after"] - result["before"]
    else:
        # Grouped totals
        group_cols = list(group_cols)
        before_grouped = before.groupby(group_cols)[value_cols].sum()
        after_grouped = after.groupby(group_cols)[value_cols].sum()

        result = pd.concat(
            [
                before_grouped.add_suffix("_before"),
                after_grouped.add_suffix("_after"),
            ],
            axis=1,
        ).fillna(0)

        for col in value_cols:
            result[f"{col}_delta"] = result[f"{col}_after"] - result[f"{col}_before"]

        result = result.reset_index()

    audit_log("reconciliation_check", before=None, after=result)
    return result
