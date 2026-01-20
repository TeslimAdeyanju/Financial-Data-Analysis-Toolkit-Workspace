"""
Column name cleaning and standardisation utilities.

This module contains functions used to clean and standardise
DataFrame column headers for reliable downstream analysis.
"""

from __future__ import annotations
from typing import Any
import pandas as pd

from fda_toolkit.utils.logging import audit_log
from fda_toolkit.registry import register_function


@register_function(
    name="clean_column_headers",
    category="Column Management",
    module="core.columns",
)
def clean_column_headers(
    df: pd.DataFrame,
    lowercase: bool = True,
    replace_spaces_with: str = "_",
    remove_non_alnum: bool = True,
    copy: bool = True,
) -> pd.DataFrame:
    """
    Standardize column headers with flexible options.

    Performs the following steps in order:
    - Strip leading/trailing whitespace
    - Normalize consecutive spaces
    - Optional: convert to lowercase
    - Optional: replace spaces with specified character
    - Optional: remove non-alphanumeric characters
    - Handle duplicate column names by appending suffixes

    Args:
        df (pd.DataFrame): Input DataFrame
        lowercase (bool): Convert headers to lowercase. Default: True
        replace_spaces_with (str): Character replacing spaces.
            Default: "_"
        remove_non_alnum (bool): Remove non-alphanumeric chars.
            Default: True
        copy (bool): Return a copy or modify in-place. Default: True

    Returns:
        pd.DataFrame: DataFrame with standardized column headers

    Raises:
        TypeError: If input is not a pandas DataFrame

    Example:
        >>> df = pd.DataFrame({'Name ': [1], 'Age (years)': [2]})
        >>> clean_column_headers(df).columns.tolist()
        ['name', 'age_years']
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    if copy:
        df = df.copy()

    cols = df.columns.astype(str).str.strip()

    if lowercase:
        cols = cols.str.lower()

    cols = cols.str.replace(r"\s+", replace_spaces_with, regex=True)

    if remove_non_alnum:
        pattern = rf"[^a-z0-9_{replace_spaces_with}]"
        cols = cols.str.replace(pattern, "", regex=True)

    pattern_dup = rf"{replace_spaces_with}+"
    cols = cols.str.replace(pattern_dup, replace_spaces_with, regex=True)
    cols = cols.str.strip(replace_spaces_with)

    # Handle duplicates
    seen: dict[Any, int] = {}
    new_cols: list[Any] = []
    for col in cols:
        count: int = seen.get(col, 0)
        new_cols.append(col if count == 0 else f"{col}_{count}")
        seen[col] = count + 1

    df.columns = new_cols
    audit_log("clean_column_headers", before=None, after=df)

    return df


@register_function(
    name="make_unique_columns",
    category="Column Management",
    module="core.columns",
)
def make_unique_columns(df: pd.DataFrame, copy: bool = True) -> pd.DataFrame:
    """
    Ensure column names are unique by appending numeric suffixes.

    For duplicate column names, appends _1, _2, etc. to create uniqueness.
    The first occurrence keeps its original name.

    Args:
        df (pd.DataFrame): Input DataFrame
        copy (bool): Return a copy or modify in-place. Default: True

    Returns:
        pd.DataFrame: DataFrame with unique column names

    Raises:
        TypeError: If input is not a pandas DataFrame

    Example:
        >>> df = pd.DataFrame({'A': [1], 'B': [2], 'A': [3]})  # Dup 'A'
        >>> make_unique_columns(df).columns.tolist()
        ['A', 'B', 'A_1']
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    if copy:
        df = df.copy()

    seen: dict[Any, int] = {}
    new_cols: list[Any] = []
    for col in df.columns:
        count: int = seen.get(col, 0)
        new_cols.append(col if count == 0 else f"{col}_{count}")
        seen[col] = count + 1

    df.columns = new_cols
    audit_log("make_unique_columns", before=None, after=df)

    return df
