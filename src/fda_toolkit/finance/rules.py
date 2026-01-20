"""
Finance-specific business rules and validation utilities.

This module provides functions to apply financial domain logic including
outlier detection, sign validation, and balanced entry checks.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, Optional

import pandas as pd
import numpy as np

from fda_toolkit.utils.logging import audit_log
from fda_toolkit.registry import register_function


@register_function(
    name="impute_by_rule",
    category="Finance",
    module="finance.rules",
)
def impute_by_rule(
    df: pd.DataFrame,
    rules: Dict[str, Dict[str, Any]],
    copy: bool = True,
) -> pd.DataFrame:
    """
    Impute missing values using explicit business rules.

    Applies domain-specific rules to fill missing values based on
    conditions and fixed values defined in the rules dictionary.

    Args:
        df (pd.DataFrame): Input DataFrame
        rules (dict): Rules mapping column names to imputation strategies
                     Example: {'amount': {'value': 0}, 'status': {'value': 'Unknown'}}
        copy (bool): Return a copy or modify in-place. Default: True

    Returns:
        pd.DataFrame: DataFrame with imputed values

    Raises:
        TypeError: If input is not a DataFrame or rules is not dict

    Example:
        >>> df = pd.DataFrame({'amount': [1.0, np.nan, 3.0]})
        >>> impute_by_rule(df, {'amount': {'value': 0}})['amount'].tolist()
        [1.0, 0.0, 3.0]
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    if not isinstance(rules, dict):
        raise TypeError("Rules must be a dictionary")

    if copy:
        df = df.copy()

    for col, rule in rules.items():
        if col in df.columns and "value" in rule:
            df[col].fillna(rule["value"], inplace=True)

    audit_log("impute_by_rule", before=None, after=df)
    return df


@register_function(
    name="detect_outliers_groupwise",
    category="Finance",
    module="finance.rules",
)
def detect_outliers_groupwise(
    df: pd.DataFrame,
    value_col: str,
    group_cols: Iterable[str],
    method: str = "iqr",
    copy: bool = True,
) -> pd.DataFrame:
    """
    Detect outliers within groups such as merchant or cost centre.

    Identifies outliers relative to group statistics rather than
    global statistics, useful for analyzing grouped financial data.

    Args:
        df (pd.DataFrame): Input DataFrame
        value_col (str): Column with values to test
        group_cols (Iterable[str]): Grouping columns (e.g., merchant, department)
        method (str): Detection method - 'iqr' or 'zscore'. Default: 'iqr'
        copy (bool): Return a copy or modify in-place. Default: True

    Returns:
        pd.DataFrame: DataFrame with added 'is_outlier' column

    Raises:
        TypeError: If input is not a DataFrame
        ValueError: If columns don't exist or method is unknown

    Example:
        >>> df = pd.DataFrame({
        ...     'merchant': ['A', 'A', 'B', 'B'],
        ...     'amount': [10, 100, 50, 51]
        ... })
        >>> detect_outliers_groupwise(df, 'amount', ['merchant'])
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    group_cols = list(group_cols)
    required = group_cols + [value_col]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Columns not found: {missing}")

    if copy:
        df = df.copy()

    def detect_outlier_group(group):
        if method == "iqr":
            Q1 = group[value_col].quantile(0.25)
            Q3 = group[value_col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            return (group[value_col] < lower) | (group[value_col] > upper)
        elif method == "zscore":
            mean = group[value_col].mean()
            std = group[value_col].std()
            z_scores = (group[value_col] - mean).abs() / std
            return z_scores > 3.0
        else:
            raise ValueError(f"Unknown method: {method}")

    df["is_outlier"] = df.groupby(group_cols, group_keys=False).apply(
        detect_outlier_group
    )

    audit_log("detect_outliers_groupwise", before=None, after=df)
    return df


@register_function(
    name="seasonality_aware_outliers",
    category="Finance",
    module="finance.rules",
)
def seasonality_aware_outliers(
    df: pd.DataFrame,
    date_col: str,
    value_col: str,
    period: str = "M",
    method: str = "iqr",
    copy: bool = True,
) -> pd.DataFrame:
    """
    Detect outliers with seasonality awareness for time series.

    Detects outliers separately within each season/period to avoid
    flagging values that are normal for their season.

    Args:
        df (pd.DataFrame): Input DataFrame
        date_col (str): Date column for grouping by period
        value_col (str): Column with values to test
        period (str): Period to group by - 'M' (month), 'Q' (quarter), 'Y' (year). Default: 'M'
        method (str): Detection method - 'iqr' or 'zscore'. Default: 'iqr'
        copy (bool): Return a copy or modify in-place. Default: True

    Returns:
        pd.DataFrame: DataFrame with added 'is_outlier' column

    Raises:
        TypeError: If input is not a DataFrame
        ValueError: If columns don't exist or period is invalid

    Example:
        >>> df = pd.DataFrame({
        ...     'date': pd.date_range('2020-01-01', periods=12),
        ...     'amount': [10]*12 + [1000]
        ... })
        >>> seasonality_aware_outliers(df, 'date', 'amount', period='M')
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    if date_col not in df.columns or value_col not in df.columns:
        raise ValueError(f"Columns not found")

    if copy:
        df = df.copy()

    if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
        df[date_col] = pd.to_datetime(df[date_col])

    # Extract period
    if period == "M":
        df["_period"] = df[date_col].dt.to_period("M")
    elif period == "Q":
        df["_period"] = df[date_col].dt.to_period("Q")
    elif period == "Y":
        df["_period"] = df[date_col].dt.to_period("Y")
    else:
        raise ValueError(f"Unknown period: {period}")

    # Detect outliers within each period
    def detect_in_period(group):
        if method == "iqr":
            Q1 = group[value_col].quantile(0.25)
            Q3 = group[value_col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            return (group[value_col] < lower) | (group[value_col] > upper)
        elif method == "zscore":
            mean = group[value_col].mean()
            std = group[value_col].std()
            z_scores = (group[value_col] - mean).abs() / std
            return z_scores > 3.0
        else:
            raise ValueError(f"Unknown method: {method}")

    df["is_outlier"] = df.groupby("_period", group_keys=False).apply(detect_in_period)
    df = df.drop("_period", axis=1)

    audit_log("seasonality_aware_outliers", before=None, after=df)
    return df


@register_function(
    name="validate_sign_conventions",
    category="Finance",
    module="finance.rules",
)
def validate_sign_conventions(
    df: pd.DataFrame,
    rules: Dict[str, str],
) -> pd.DataFrame:
    """
    Validate sign conventions for numeric columns.

    Checks that values in specified columns conform to sign rules
    (e.g., revenue should be non-negative, refunds non-positive).

    Args:
        df (pd.DataFrame): Input DataFrame
        rules (dict): Mapping of column to sign rule. Options:
                     'non_negative' (>= 0), 'non_positive' (<= 0), 'positive' (> 0), 'negative' (< 0)
                     Example: {'revenue': 'non_negative', 'refund': 'non_positive'}

    Returns:
        pd.DataFrame: Boolean Series indicating violations per row

    Raises:
        TypeError: If input is not a DataFrame
        ValueError: If columns don't exist or rules are invalid

    Example:
        >>> df = pd.DataFrame({'revenue': [10, -5], 'refund': [-10, 5]})
        >>> validate_sign_conventions(df, {'revenue': 'non_negative'})
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    violations = pd.DataFrame(False, index=df.index, columns=rules.keys())

    for col, rule in rules.items():
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found")

        if rule == "non_negative":
            violations[col] = df[col] < 0
        elif rule == "non_positive":
            violations[col] = df[col] > 0
        elif rule == "positive":
            violations[col] = df[col] <= 0
        elif rule == "negative":
            violations[col] = df[col] >= 0
        else:
            raise ValueError(f"Unknown rule: {rule}")

    audit_log("validate_sign_conventions", before=None, after=violations)
    return violations


@register_function(
    name="check_balanced_entries",
    category="Finance",
    module="finance.rules",
)
def check_balanced_entries(
    df: pd.DataFrame,
    debit_col: str = "debit",
    credit_col: str = "credit",
    group_cols: Optional[Iterable[str]] = None,
    tolerance: float = 0.0,
) -> pd.DataFrame:
    """
    Check that debit equals credit at row or grouped level.

    Validates accounting entries where debits must equal credits,
    optionally allowing a small tolerance for rounding.

    Args:
        df (pd.DataFrame): Input DataFrame with debit and credit columns
        debit_col (str): Name of debit column. Default: 'debit'
        credit_col (str): Name of credit column. Default: 'credit'
        group_cols (Iterable[str]): Columns to group by for validation. Default: None (row-level)
        tolerance (float): Maximum allowed imbalance. Default: 0.0

    Returns:
        pd.DataFrame: Boolean Series indicating imbalanced rows/groups

    Raises:
        TypeError: If input is not a DataFrame
        ValueError: If columns don't exist

    Example:
        >>> df = pd.DataFrame({'debit': [100, 100], 'credit': [100, 99]})
        >>> check_balanced_entries(df, tolerance=0.01)
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    if debit_col not in df.columns or credit_col not in df.columns:
        raise ValueError(f"Columns '{debit_col}' and/or '{credit_col}' not found")

    if group_cols is None:
        # Row-level check
        imbalanced = (df[debit_col] - df[credit_col]).abs() > tolerance
    else:
        # Group-level check
        group_cols = list(group_cols)
        imbalanced = df.groupby(group_cols).apply(
            lambda x: (x[debit_col].sum() - x[credit_col].sum()).abs() > tolerance
        ).reset_index(drop=True)

    audit_log("check_balanced_entries", before=None, after=imbalanced)
    return imbalanced
