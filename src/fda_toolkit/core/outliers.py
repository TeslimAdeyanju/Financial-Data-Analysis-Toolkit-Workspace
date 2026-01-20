"""
Outlier detection and handling utilities.

This module provides functions to detect, flag, and handle outliers
using statistical methods like IQR and z-score.
"""

from __future__ import annotations

import pandas as pd

from fda_toolkit.utils.logging import audit_log
from fda_toolkit.registry import register_function


@register_function(
    name="detect_outliers_iqr",
    category="Outlier Detection",
    module="core.outliers",
)
def detect_outliers_iqr(
    s: pd.Series,
    k: float = 1.5,
) -> pd.Series:
    """
    Return boolean mask for IQR-based outliers.

    Uses the Interquartile Range (IQR) method: identifies values
    outside [Q1 - k*IQR, Q3 + k*IQR] as outliers.

    Args:
        s (pd.Series): Input numeric Series
        k (float): IQR multiplier for bounds. Default: 1.5

    Returns:
        pd.Series: Boolean Series marking outliers

    Raises:
        TypeError: If Series is not numeric

    Example:
        >>> s = pd.Series([1, 2, 3, 4, 100])
        >>> detect_outliers_iqr(s).sum()
        1
    """
    if not pd.api.types.is_numeric_dtype(s):
        raise TypeError("Series must be numeric")

    Q1 = s.quantile(0.25)
    Q3 = s.quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - k * IQR
    upper_bound = Q3 + k * IQR

    outliers = (s < lower_bound) | (s > upper_bound)

    audit_log("detect_outliers_iqr", before=None, after=outliers)
    return outliers


@register_function(
    name="remove_outliers_iqr",
    category="Outlier Detection",
    module="core.outliers",
)
def remove_outliers_iqr(
    df: pd.DataFrame,
    column: str,
    k: float = 1.5,
    copy: bool = True,
) -> pd.DataFrame:
    """
    Remove rows where column is an IQR outlier.

    Args:
        df (pd.DataFrame): Input DataFrame
        column (str): Column name to check for outliers
        k (float): IQR multiplier. Default: 1.5
        copy (bool): Return a copy or modify in-place. Default: True

    Returns:
        pd.DataFrame: DataFrame with outlier rows removed

    Raises:
        TypeError: If column is not numeric or not found

    Example:
        >>> df = pd.DataFrame({'A': [1, 2, 3, 4, 100]})
        >>> remove_outliers_iqr(df, 'A').shape[0]
        4
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found")

    if copy:
        df = df.copy()

    outlier_mask = detect_outliers_iqr(df[column], k=k)
    result: pd.DataFrame = df[~outlier_mask]  # type: ignore[assignment]

    audit_log("remove_outliers_iqr", before=None, after=result)
    return result


@register_function(
    name="remove_outliers_zscore",
    category="Outlier Detection",
    module="core.outliers",
)
def remove_outliers_zscore(
    df: pd.DataFrame,
    column: str,
    z: float = 3.0,
    copy: bool = True,
) -> pd.DataFrame:
    """
    Remove rows where column exceeds z-score threshold.

    Removes values where |z-score| > threshold (default 3.0 sigma).

    Args:
        df (pd.DataFrame): Input DataFrame
        column (str): Column name to check
        z (float): Z-score threshold. Default: 3.0
        copy (bool): Return a copy or modify in-place. Default: True

    Returns:
        pd.DataFrame: DataFrame with high z-score rows removed

    Raises:
        TypeError: If column is not numeric or not found

    Example:
        >>> df = pd.DataFrame({'A': [1, 2, 3, 4, 100]})
        >>> remove_outliers_zscore(df, 'A', z=2.5).shape[0]
        4
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found")

    if copy:
        df = df.copy()

    mean = df[column].mean()
    std = df[column].std()

    z_scores = (df[column] - mean).abs() / std
    result: pd.DataFrame = df[z_scores <= z]  # type: ignore[assignment]

    audit_log("remove_outliers_zscore", before=None, after=result)
    return result


@register_function(
    name="flag_outliers",
    category="Outlier Detection",
    module="core.outliers",
)
def flag_outliers(
    df: pd.DataFrame,
    column: str,
    method: str = "iqr",
    copy: bool = True,
) -> pd.DataFrame:
    """
    Add an is_outlier column rather than dropping data.

    Flags outliers for later analysis while preserving all rows.

    Args:
        df (pd.DataFrame): Input DataFrame
        column (str): Column name to check
        method (str): Detection method - 'iqr' or 'zscore'. Default: 'iqr'
        copy (bool): Return a copy or modify in-place. Default: True

    Returns:
        pd.DataFrame: DataFrame with added 'is_outlier' column

    Raises:
        TypeError: If column is not numeric or not found
        ValueError: If method is unknown

    Example:
        >>> df = pd.DataFrame({'A': [1, 2, 3, 4, 100]})
        >>> flag_outliers(df, 'A')['is_outlier'].sum()
        1
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found")

    if copy:
        df = df.copy()

    if method == "iqr":
        df["is_outlier"] = detect_outliers_iqr(df[column])
    elif method == "zscore":
        mean = df[column].mean()
        std = df[column].std()
        z_scores = (df[column] - mean).abs() / std
        df["is_outlier"] = z_scores > 3.0
    else:
        raise ValueError(f"Unknown method: {method}")

    audit_log("flag_outliers", before=None, after=df)
    return df


@register_function(
    name="cap_outliers",
    category="Outlier Detection",
    module="core.outliers",
)
def cap_outliers(
    df: pd.DataFrame,
    column: str,
    lower_quantile: float = 0.01,
    upper_quantile: float = 0.99,
    copy: bool = True,
) -> pd.DataFrame:
    """
    Cap outliers using quantiles.

    Limits values to the specified quantile bounds.

    Args:
        df (pd.DataFrame): Input DataFrame
        column (str): Column name to cap
        lower_quantile (float): Lower bound quantile. Default: 0.01
        upper_quantile (float): Upper bound quantile. Default: 0.99
        copy (bool): Return a copy or modify in-place. Default: True

    Returns:
        pd.DataFrame: DataFrame with capped values

    Raises:
        TypeError: If column is not numeric or not found
        ValueError: If quantiles are out of range [0, 1]

    Example:
        >>> df = pd.DataFrame({'A': [1, 2, 3, 4, 100]})
        >>> cap_outliers(df, 'A')['A'].max()
        4.0
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found")
    if not (0 <= lower_quantile <= upper_quantile <= 1):
        raise ValueError("Quantiles must be in [0, 1]")

    if copy:
        df = df.copy()

    lower = df[column].quantile(lower_quantile)
    upper = df[column].quantile(upper_quantile)

    df[column] = df[column].clip(lower=lower, upper=upper)

    audit_log("cap_outliers", before=None, after=df)
    return df


@register_function(
    name="winsorize_outliers",
    category="Outlier Detection",
    module="core.outliers",
)
def winsorize_outliers(
    df: pd.DataFrame,
    column: str,
    limits: tuple[float, float] = (0.01, 0.01),
    copy: bool = True,
) -> pd.DataFrame:
    """
    Winsorize outliers using quantile clipping.

    Replaces extreme values with the specified percentiles.
    Winsorization reduces the impact of outliers without losing data.

    Args:
        df (pd.DataFrame): Input DataFrame
        column (str): Column name to winsorize
        limits (tuple[float, float]): (lower, upper) quantiles.
            Default: (0.01, 0.01)
        copy (bool): Return a copy or modify in-place. Default: True

    Returns:
        pd.DataFrame: DataFrame with winsorized values

    Raises:
        TypeError: If column is not numeric or not found
        ValueError: If limits are out of range [0, 1]

    Example:
        >>> df = pd.DataFrame({'A': [1, 2, 3, 4, 100]})
        >>> winsorize_outliers(df, 'A', limits=(0.05, 0.05))['A'].max()
        3.96
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found")

    if copy:
        df = df.copy()

    lower, upper = limits
    if not (0 <= lower <= 0.5 and 0 <= upper <= 0.5):
        raise ValueError("Limits must be in [0, 0.5]")

    lower_bound = df[column].quantile(lower)
    upper_bound = df[column].quantile(1 - upper)

    df[column] = df[column].clip(lower=lower_bound, upper=upper_bound)

    audit_log("winsorize_outliers", before=None, after=df)
    return df
