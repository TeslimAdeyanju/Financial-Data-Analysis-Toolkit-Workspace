"""
Date/time feature engineering utilities.

This module provides functions to extract date features, create period keys,
and build fiscal calendar and lag features for time-series analysis.
"""

from __future__ import annotations

from typing import Iterable, Optional

import pandas as pd

from fda_toolkit.utils.logging import audit_log
from fda_toolkit.registry import register_function


@register_function(
    name="extract_date_features",
    category="Feature Engineering",
    module="features.datetime",
)
def extract_date_features(
    df: pd.DataFrame,
    date_col: str,
    prefix: Optional[str] = None,
    copy: bool = True,
) -> pd.DataFrame:
    """
    Extract common date features such as year, month, quarter.

    Creates new columns for year, quarter, month, day, day of week,
    day of year, and week number.

    Args:
        df (pd.DataFrame): Input DataFrame
        date_col (str): Name of datetime column
        prefix (str): Prefix for new column names. Default: date_col + "_"
        copy (bool): Return a copy or modify in-place. Default: True

    Returns:
        pd.DataFrame: DataFrame with extracted date features

    Raises:
        TypeError: If input is not a DataFrame
        ValueError: If date_col doesn't exist or is not datetime

    Example:
        >>> df = pd.DataFrame({'date': pd.date_range('2020-01-01', periods=3)})
        >>> extract_date_features(df, 'date').columns.tolist()
        ['date', 'date_year', 'date_quarter', 'date_month', ...]
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    if date_col not in df.columns:
        raise ValueError(f"Column '{date_col}' not found")

    if copy:
        df = df.copy()

    if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
        df[date_col] = pd.to_datetime(df[date_col])

    prefix = prefix or f"{date_col}_"

    df[f"{prefix}year"] = df[date_col].dt.year
    df[f"{prefix}quarter"] = df[date_col].dt.quarter
    df[f"{prefix}month"] = df[date_col].dt.month
    df[f"{prefix}day"] = df[date_col].dt.day
    df[f"{prefix}dayofweek"] = df[date_col].dt.dayofweek
    df[f"{prefix}dayofyear"] = df[date_col].dt.dayofyear
    df[f"{prefix}weekofyear"] = df[date_col].dt.isocalendar().week

    audit_log("extract_date_features", before=None, after=df)
    return df


@register_function(
    name="create_period_keys",
    category="Feature Engineering",
    module="features.datetime",
)
def create_period_keys(
    df: pd.DataFrame,
    date_col: str,
    period: str = "M",
    key_name: str = "period_key",
    copy: bool = True,
) -> pd.DataFrame:
    """
    Create period keys like yyyymm.

    Generates a unique identifier for each period (year-month, year-quarter, etc.).

    Args:
        df (pd.DataFrame): Input DataFrame
        date_col (str): Name of datetime column
        period (str): Period frequency - 'M' (month), 'Q' (quarter), 'Y' (year). Default: 'M'
        key_name (str): Name of new column. Default: 'period_key'
        copy (bool): Return a copy or modify in-place. Default: True

    Returns:
        pd.DataFrame: DataFrame with period key column

    Raises:
        TypeError: If input is not a DataFrame
        ValueError: If date_col doesn't exist or period is invalid

    Example:
        >>> df = pd.DataFrame({'date': pd.date_range('2020-01-01', periods=3)})
        >>> create_period_keys(df, 'date', period='M')
        period_key
        202001
        202001
        202002
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    if date_col not in df.columns:
        raise ValueError(f"Column '{date_col}' not found")

    if copy:
        df = df.copy()

    if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
        df[date_col] = pd.to_datetime(df[date_col])

    if period == "M":
        df[key_name] = df[date_col].dt.strftime("%Y%m")
    elif period == "Q":
        df[key_name] = df[date_col].dt.strftime("%Y") + "Q" + df[date_col].dt.quarter.astype(str)
    elif period == "Y":
        df[key_name] = df[date_col].dt.strftime("%Y")
    else:
        raise ValueError(f"Unknown period: {period}")

    audit_log("create_period_keys", before=None, after=df)
    return df


@register_function(
    name="create_fiscal_calendar_features",
    category="Feature Engineering",
    module="features.datetime",
)
def create_fiscal_calendar_features(
    df: pd.DataFrame,
    date_col: str,
    fiscal_year_start_month: int = 4,
    copy: bool = True,
) -> pd.DataFrame:
    """
    Create fiscal year and fiscal period features.

    Useful for organizations that use fiscal calendars different from
    the calendar year (e.g., fiscal year starting in April).

    Args:
        df (pd.DataFrame): Input DataFrame
        date_col (str): Name of datetime column
        fiscal_year_start_month (int): Month where fiscal year starts. Default: 4 (April)
        copy (bool): Return a copy or modify in-place. Default: True

    Returns:
        pd.DataFrame: DataFrame with fiscal_year and fiscal_period columns

    Raises:
        TypeError: If input is not a DataFrame
        ValueError: If date_col doesn't exist or fiscal_year_start_month is invalid

    Example:
        >>> df = pd.DataFrame({'date': pd.date_range('2020-01-01', periods=12)})
        >>> create_fiscal_calendar_features(df, 'date', fiscal_year_start_month=4)
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    if date_col not in df.columns:
        raise ValueError(f"Column '{date_col}' not found")
    if not (1 <= fiscal_year_start_month <= 12):
        raise ValueError("fiscal_year_start_month must be between 1 and 12")

    if copy:
        df = df.copy()

    if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
        df[date_col] = pd.to_datetime(df[date_col])

    month = df[date_col].dt.month
    year = df[date_col].dt.year

    df["fiscal_year"] = year + (month >= fiscal_year_start_month).astype(int)
    df["fiscal_period"] = ((month - fiscal_year_start_month) % 12) + 1

    audit_log("create_fiscal_calendar_features", before=None, after=df)
    return df


@register_function(
    name="lag_features",
    category="Feature Engineering",
    module="features.datetime",
)
def lag_features(
    df: pd.DataFrame,
    group_cols: Iterable[str],
    sort_col: str,
    value_col: str,
    lags: Iterable[int] = (1, 3, 12),
    copy: bool = True,
) -> pd.DataFrame:
    """
    Create lag features for forecasting and anomaly detection.

    Generates lagged versions of a value column, grouped by key columns
    and sorted by a date column.

    Args:
        df (pd.DataFrame): Input DataFrame
        group_cols (Iterable[str]): Columns to group by
        sort_col (str): Column to sort by (typically date)
        value_col (str): Column to lag
        lags (Iterable[int]): Lag periods to create. Default: (1, 3, 12)
        copy (bool): Return a copy or modify in-place. Default: True

    Returns:
        pd.DataFrame: DataFrame with lagged columns

    Raises:
        TypeError: If input is not a DataFrame
        ValueError: If required columns don't exist

    Example:
        >>> df = pd.DataFrame({
        ...     'group': ['A']*3,
        ...     'date': pd.date_range('2020-01-01', periods=3),
        ...     'value': [10, 20, 30]
        ... })
        >>> lag_features(df, ['group'], 'date', 'value', lags=[1])
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    group_cols = list(group_cols)
    required = group_cols + [sort_col, value_col]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Columns not found: {missing}")

    if copy:
        df = df.copy()

    df = df.sort_values([*group_cols, sort_col])

    for lag in lags:
        df[f"{value_col}_lag_{lag}"] = df.groupby(group_cols)[value_col].shift(lag)

    audit_log("lag_features", before=None, after=df)
    return df
