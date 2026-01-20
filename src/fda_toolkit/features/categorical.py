"""
Categorical feature engineering utilities.

This module provides functions to reduce cardinality, handle rare categories,
and encode categorical variables for modeling.
"""

from __future__ import annotations

from typing import Iterable, Optional

import pandas as pd

from fda_toolkit.utils.logging import audit_log
from fda_toolkit.registry import register_function


@register_function(
    name="limit_cardinality",
    category="Feature Engineering",
    module="features.categorical",
)
def limit_cardinality(
    s: pd.Series,
    top_n: int = 20,
    other_label: str = "Other",
) -> pd.Series:
    """
    Keep top N categories and group the rest into Other.

    Useful for reducing dimensionality when a categorical column
    has very high cardinality.

    Args:
        s (pd.Series): Input categorical Series
        top_n (int): Number of top categories to keep. Default: 20
        other_label (str): Label for grouped rare categories. Default: "Other"

    Returns:
        pd.Series: Series with reduced cardinality

    Raises:
        TypeError: If Series is not object dtype
        ValueError: If top_n is less than 1

    Example:
        >>> s = pd.Series(['A', 'B', 'C'] * 10 + ['D', 'E', 'F', 'G', 'H'])
        >>> limit_cardinality(s, top_n=3).nunique()
        4
    """
    if s.dtype != "object":
        raise TypeError("Series must be object/string dtype")
    if top_n < 1:
        raise ValueError("top_n must be at least 1")

    s = s.copy()

    top_categories = s.value_counts().head(top_n).index
    s = s.where(s.isin(top_categories), other_label)

    audit_log("limit_cardinality", before=None, after=s)
    return s


@register_function(
    name="rare_category_handler",
    category="Feature Engineering",
    module="features.categorical",
)
def rare_category_handler(
    s: pd.Series,
    min_count: int = 10,
    other_label: str = "Other",
) -> pd.Series:
    """
    Replace rare categories with Other.

    Categories appearing fewer than min_count times are grouped together.

    Args:
        s (pd.Series): Input categorical Series
        min_count (int): Minimum frequency threshold. Default: 10
        other_label (str): Label for rare categories. Default: "Other"

    Returns:
        pd.Series: Series with rare categories consolidated

    Raises:
        TypeError: If Series is not object dtype
        ValueError: If min_count is less than 1

    Example:
        >>> s = pd.Series(['A']*20 + ['B']*5 + ['C']*3)
        >>> rare_category_handler(s, min_count=10).value_counts()
        A       20
        Other    8
    """
    if s.dtype != "object":
        raise TypeError("Series must be object/string dtype")
    if min_count < 1:
        raise ValueError("min_count must be at least 1")

    s = s.copy()

    value_counts = s.value_counts()
    rare = value_counts[value_counts < min_count].index
    s = s.where(~s.isin(rare), other_label)

    audit_log("rare_category_handler", before=None, after=s)
    return s


@register_function(
    name="encode_categorical_variables",
    category="Feature Engineering",
    module="features.categorical",
)
def encode_categorical_variables(
    df: pd.DataFrame,
    columns: Iterable[str],
    drop_first: bool = False,
    copy: bool = True,
) -> pd.DataFrame:
    """
    One-hot encode categorical columns.

    Creates binary indicator columns for each category value.

    Args:
        df (pd.DataFrame): Input DataFrame
        columns (Iterable[str]): Categorical column names to encode
        drop_first (bool): Drop first category to avoid multicollinearity. Default: False
        copy (bool): Return a copy or modify in-place. Default: True

    Returns:
        pd.DataFrame: DataFrame with encoded columns

    Raises:
        TypeError: If input is not a DataFrame
        ValueError: If columns don't exist

    Example:
        >>> df = pd.DataFrame({'Color': ['Red', 'Blue', 'Red']})
        >>> encode_categorical_variables(df, ['Color']).shape[1]
        2
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    cols = list(columns)
    missing = [col for col in cols if col not in df.columns]
    if missing:
        raise ValueError(f"Columns not found: {missing}")

    if copy:
        df = df.copy()

    df = pd.get_dummies(df, columns=cols, drop_first=drop_first)

    audit_log("encode_categorical_variables", before=None, after=df)
    return df
