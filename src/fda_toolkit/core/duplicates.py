"""
Duplicate detection and removal utilities.

This module provides functions to find, analyze, and remove
duplicate rows based on various criteria and strategies.
"""

from __future__ import annotations

from typing import Iterable, Optional

import pandas as pd

from fda_toolkit.utils.logging import audit_log
from fda_toolkit.registry import register_function


@register_function(
    name="find_duplicates",
    category="Data Quality",
    module="core.duplicates",
)
def find_duplicates(
    df: pd.DataFrame,
    subset: Optional[Iterable[str]] = None,
    keep: str = "first",
) -> pd.DataFrame:
    """
    Return duplicated rows based on subset of columns.

    Marks all rows that are duplicates based on the specified columns.
    By default, the first occurrence is not marked as duplicate.

    Args:
        df (pd.DataFrame): Input DataFrame
        subset (Iterable[str]): Column names to consider for duplicates.
                               If None, all columns are used. Default: None
        keep (str): Which duplicate to mark as False - 'first', 'last', or False (all).
                   Default: 'first'

    Returns:
        pd.DataFrame: Boolean Series indicating duplicate rows

    Raises:
        TypeError: If input is not a DataFrame
        ValueError: If subset columns don't exist

    Example:
        >>> df = pd.DataFrame({'A': [1, 1, 2], 'B': [1, 1, 2]})
        >>> find_duplicates(df).tolist()
        [False, True, False]
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    if subset is not None:
        subset = list(subset)
        missing = [col for col in subset if col not in df.columns]
        if missing:
            raise ValueError(f"Columns not found: {missing}")

    dup_mask = df.duplicated(subset=subset, keep=keep)

    audit_log("find_duplicates", before=None, after=dup_mask)
    return dup_mask


@register_function(
    name="deduplicate_by_priority",
    category="Data Quality",
    module="core.duplicates",
)
def deduplicate_by_priority(
    df: pd.DataFrame,
    subset: Iterable[str],
    sort_by: Iterable[str],
    keep: str = "last",
    copy: bool = True,
) -> pd.DataFrame:
    """
    Deduplicate using an explicit priority rule.

    For rows that are duplicates based on 'subset', keeps the row with
    the highest priority according to 'sort_by' columns.

    Args:
        df (pd.DataFrame): Input DataFrame
        subset (Iterable[str]): Columns defining duplicates
        sort_by (Iterable[str]): Columns to sort by (determines priority)
        keep (str): Which to keep - 'first' or 'last' after sorting. Default: 'last'
        copy (bool): Return a copy or modify in-place. Default: True

    Returns:
        pd.DataFrame: Deduplicated DataFrame

    Raises:
        TypeError: If input is not a DataFrame
        ValueError: If subset or sort_by columns don't exist

    Example:
        >>> df = pd.DataFrame({
        ...     'id': [1, 1, 2],
        ...     'date': ['2020-01-01', '2020-01-02', '2020-01-01'],
        ...     'value': [10, 20, 30]
        ... })
        >>> deduplicate_by_priority(
        ...     df, subset=['id'], sort_by=['date'], keep='last'
        ... ).shape
        (2, 3)
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    if copy:
        df = df.copy()

    subset = list(subset)
    sort_by = list(sort_by)

    missing_subset = [col for col in subset if col not in df.columns]
    missing_sort = [col for col in sort_by if col not in df.columns]

    if missing_subset or missing_sort:
        raise ValueError(
            f"Missing columns - subset: {missing_subset}, sort_by: {missing_sort}"
        )

    df = df.sort_values(by=sort_by, na_position="last")
    df = df.drop_duplicates(subset=subset, keep=keep)

    audit_log("deduplicate_by_priority", before=None, after=df)
    return df


@register_function(
    name="remove_duplicates",
    category="Data Quality",
    module="core.duplicates",
)
def remove_duplicates(
    df: pd.DataFrame,
    subset: Optional[Iterable[str]] = None,
    keep: str = "first",
    copy: bool = True,
) -> pd.DataFrame:
    """
    Remove duplicates using pandas drop_duplicates.

    Removes duplicate rows based on the specified column subset.
    The first occurrence is kept by default.

    Args:
        df (pd.DataFrame): Input DataFrame
        subset (Iterable[str]): Columns to consider for duplicates.
                               If None, all columns are used. Default: None
        keep (str): Which duplicate to keep - 'first', 'last', or False (remove all).
                   Default: 'first'
        copy (bool): Return a copy or modify in-place. Default: True

    Returns:
        pd.DataFrame: DataFrame with duplicates removed

    Raises:
        TypeError: If input is not a DataFrame
        ValueError: If subset columns don't exist

    Example:
        >>> df = pd.DataFrame({'A': [1, 1, 2], 'B': [1, 1, 2]})
        >>> remove_duplicates(df).shape
        (2, 2)
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    if subset is not None:
        subset = list(subset)
        missing = [col for col in subset if col not in df.columns]
        if missing:
            raise ValueError(f"Columns not found: {missing}")

    if copy:
        df = df.copy()

    df = df.drop_duplicates(subset=subset, keep=keep)

    audit_log("remove_duplicates", before=None, after=df)
    return df
