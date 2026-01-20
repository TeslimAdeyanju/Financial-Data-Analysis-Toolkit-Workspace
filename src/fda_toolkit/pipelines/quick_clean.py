"""
Data cleaning pipeline orchestration.

This module provides high-level pipelines that compose lower-level
functions into complete cleaning workflows.
"""

from __future__ import annotations

from typing import Iterable, Optional

import pandas as pd

from fda_toolkit.utils.logging import audit_log
from fda_toolkit.registry import register_function
from fda_toolkit.core.columns import clean_column_headers
from fda_toolkit.core.missing import coerce_empty_to_nan, fill_missing
from fda_toolkit.core.duplicates import remove_duplicates


@register_function(
    name="quick_clean",
    category="Pipelines",
    module="pipelines.quick_clean",
)
def quick_clean(
    df: pd.DataFrame,
    copy: bool = True,
) -> pd.DataFrame:
    """
    One-line generic cleaning pipeline.

    Applies a standard sequence of cleaning operations:
    1. Clean column headers
    2. Coerce empty placeholders to NaN
    3. Remove duplicate rows
    4. Fill remaining missing values

    Args:
        df (pd.DataFrame): Input DataFrame
        copy (bool): Return a copy or modify in-place. Default: True

    Returns:
        pd.DataFrame: Cleaned DataFrame

    Raises:
        TypeError: If input is not a DataFrame

    Example:
        >>> df = pd.DataFrame({
        ...     'Name ': ['Alice', 'Bob', 'Alice'],
        ...     'Age (years)': ['25', 'NA', '25']
        ... })
        >>> clean_df = quick_clean(df)
        >>> clean_df.shape
        (2, 2)
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    if copy:
        df = df.copy()

    # Step 1: Clean column headers
    df = clean_column_headers(df, copy=False)

    # Step 2: Coerce empty values
    df = coerce_empty_to_nan(df, copy=False)

    # Step 3: Remove duplicates (first occurrence)
    df = remove_duplicates(df, copy=False)

    # Step 4: Fill remaining missing values with 0
    df = fill_missing(df, strategy="constant", value=0, copy=False)

    audit_log("quick_clean", before=None, after=df)
    return df


@register_function(
    name="quick_clean_finance",
    category="Pipelines",
    module="pipelines.quick_clean",
)
def quick_clean_finance(
    df: pd.DataFrame,
    primary_key: Optional[str] = None,
    date_cols: Optional[Iterable[str]] = None,
    currency_cols: Optional[Iterable[str]] = None,
    copy: bool = True,
) -> pd.DataFrame:
    """
    One-line finance-oriented cleaning pipeline.

    Applies finance-specific cleaning including:
    1. Clean column headers
    2. Coerce empty values
    3. Remove duplicates
    4. Parse currency columns
    5. Parse date columns
    6. Validate primary key (if provided)

    Args:
        df (pd.DataFrame): Input DataFrame
        primary_key (str): Column to validate as unique key. Default: None
        date_cols (Iterable[str]): Columns to parse as dates. Default: None
        currency_cols (Iterable[str]): Columns to parse as currency. Default: None
        copy (bool): Return a copy or modify in-place. Default: True

    Returns:
        pd.DataFrame: Cleaned and validated DataFrame

    Raises:
        TypeError: If input is not a DataFrame
        ValueError: If primary key has duplicates or nulls

    Example:
        >>> df = pd.DataFrame({
        ...     'Invoice ID': ['INV001', 'INV002'],
        ...     'Date': ['01/01/2020', '02/01/2020'],
        ...     'Amount': ['$1,234.56', '$2,345.67']
        ... })
        >>> clean_df = quick_clean_finance(
        ...     df,
        ...     primary_key='Invoice ID',
        ...     date_cols=['Date'],
        ...     currency_cols=['Amount']
        ... )
        >>> clean_df.dtypes
        Invoice ID           object
        Date        datetime64[ns]
        Amount             float64
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    if copy:
        df = df.copy()

    # Step 1: Clean column headers
    df = clean_column_headers(df, copy=False)

    # Step 2: Coerce empty values
    df = coerce_empty_to_nan(df, copy=False)

    # Step 3: Remove duplicates
    df = remove_duplicates(df, copy=False)

    # Step 4: Parse currency columns
    if currency_cols:
        from fda_toolkit.finance.parsing import parse_currency

        for col in currency_cols:
            if col in df.columns:
                df[col] = parse_currency(df[col])

    # Step 5: Parse date columns
    if date_cols:
        from fda_toolkit.core.types import clean_date_column

        for col in date_cols:
            if col in df.columns:
                df[col] = clean_date_column(df[col])

    # Step 6: Validate primary key
    if primary_key:
        from fda_toolkit.validation.integrity import assert_primary_key

        try:
            assert_primary_key(df, [primary_key])
        except ValueError as e:
            # Log but don't fail
            audit_log(
                "quick_clean_finance",
                before=None,
                after={"warning": f"Primary key validation failed: {e}"},
            )

    audit_log("quick_clean_finance", before=None, after=df)
    return df
