"""
Missing value detection and handling utilities.

This module provides functions to identify, analyze, and fill
missing values across DataFrames and Series.
"""

from __future__ import annotations

from typing import Any, Iterable, Optional

import numpy as np
import pandas as pd

from fda_toolkit.utils.logging import audit_log
from fda_toolkit.registry import register_function


@register_function(
    name="coerce_empty_to_nan",
    category="Data Quality",
    module="core.missing",
)
def coerce_empty_to_nan(
    df: pd.DataFrame,
    placeholders: Iterable[str] = ("", " ", "na", "n/a", "null", "none"),
    copy: bool = True,
) -> pd.DataFrame:
    """
    Convert common empty placeholders to NA (NaN/NaT).

    Identifies common text representations of missing values and converts
    them to pandas NA types for consistent missing value handling.

    Args:
        df (pd.DataFrame): Input DataFrame
        placeholders (Iterable[str]): Text values to treat as missing.
                                     Default: common placeholders
        copy (bool): Return a copy or modify in-place. Default: True

    Returns:
        pd.DataFrame: DataFrame with placeholders converted to NA

    Raises:
        TypeError: If input is not a DataFrame

    Example:
        >>> df = pd.DataFrame({'A': ['data', 'na', 'N/A'], 'B': [1, 2, 3]})
        >>> coerce_empty_to_nan(df)['A'].isna().sum()
        2
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    if copy:
        df = df.copy()

    placeholders_lower = set(str(p).lower().strip() for p in placeholders)

    for col in df.columns:
        if df[col].dtype == "object":
            mask = df[col].astype(str).str.lower().str.strip().isin(placeholders_lower)
            df.loc[mask, col] = np.nan

    audit_log("coerce_empty_to_nan", before=None, after=df)
    return df


@register_function(
    name="fill_missing",
    category="Data Quality",
    module="core.missing",
)
def fill_missing(
    df: pd.DataFrame,
    strategy: str = "constant",
    value: Any = 0,
    columns: Optional[Iterable[str]] = None,
    copy: bool = True,
) -> pd.DataFrame:
    """
    Fill missing values using a simple strategy.

    Supports filling with a constant value, forward fill, backward fill,
    or mean/median for numeric columns.

    Args:
        df (pd.DataFrame): Input DataFrame
        strategy (str): Fill strategy - 'constant', 'ffill', 'bfill', 'mean', 'median'.
                       Default: 'constant'
        value (Any): Value to use with 'constant' strategy. Default: 0
        columns (Iterable[str]): Specific columns to fill. If None, fill all. Default: None
        copy (bool): Return a copy or modify in-place. Default: True

    Returns:
        pd.DataFrame: DataFrame with missing values filled

    Raises:
        TypeError: If input is not a DataFrame
        ValueError: If strategy is unknown or columns don't exist

    Example:
        >>> df = pd.DataFrame({'A': [1, np.nan, 3], 'B': [4, 5, np.nan]})
        >>> fill_missing(df, strategy='constant', value=-999)['A'].tolist()
        [1.0, -999.0, 3.0]
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    if copy:
        df = df.copy()

    if columns is None:
        cols_to_fill = df.columns
    else:
        cols_to_fill = list(columns)
        missing = [col for col in cols_to_fill if col not in df.columns]
        if missing:
            raise ValueError(f"Columns not found: {missing}")

    if strategy == "constant":
        df[cols_to_fill] = df[cols_to_fill].fillna(value)
    elif strategy == "ffill":
        df[cols_to_fill] = df[cols_to_fill].fillna(method="ffill")
    elif strategy == "bfill":
        df[cols_to_fill] = df[cols_to_fill].fillna(method="bfill")
    elif strategy == "mean":
        for col in cols_to_fill:
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(df[col].mean())
    elif strategy == "median":
        for col in cols_to_fill:
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(df[col].median())
    else:
        raise ValueError(f"Unknown strategy: {strategy}")

    audit_log("fill_missing", before=None, after=df)
    return df
