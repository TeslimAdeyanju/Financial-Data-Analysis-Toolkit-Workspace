"""
Data security and privacy utilities.

This module provides functions to mask sensitive information and
anonymize identifiers for secure data sharing and compliance.
"""

from __future__ import annotations

from typing import Iterable, Optional
import hashlib

import pandas as pd

from fda_toolkit.utils.logging import audit_log
from fda_toolkit.registry import register_function


@register_function(
    name="mask_sensitive_fields",
    category="Utilities",
    module="utils.security",
)
def mask_sensitive_fields(
    df: pd.DataFrame,
    columns: Iterable[str],
    mask: str = "***",
    copy: bool = True,
) -> pd.DataFrame:
    """
    Mask sensitive fields such as bank details or email addresses.

    Replaces values in specified columns with a masked placeholder
    for secure data sharing.

    Args:
        df (pd.DataFrame): Input DataFrame
        columns (Iterable[str]): Column names to mask
        mask (str): Replacement value. Default: "***"
        copy (bool): Return a copy or modify in-place. Default: True

    Returns:
        pd.DataFrame: DataFrame with masked columns

    Raises:
        TypeError: If input is not a DataFrame
        ValueError: If columns don't exist

    Example:
        >>> df = pd.DataFrame({'name': ['Alice', 'Bob'], 'ssn': ['123-45-6789', '987-65-4321']})
        >>> masked = mask_sensitive_fields(df, ['ssn'], mask='###')
        >>> masked['ssn'].tolist()
        ['###', '###']
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    cols = list(columns)
    missing = [col for col in cols if col not in df.columns]
    if missing:
        raise ValueError(f"Columns not found: {missing}")

    if copy:
        df = df.copy()

    for col in cols:
        # Mask non-null values
        df[col] = df[col].where(df[col].isna(), mask)

    audit_log("mask_sensitive_fields", before=None, after=df)
    return df


@register_function(
    name="anonymize_identifiers",
    category="Utilities",
    module="utils.security",
)
def anonymize_identifiers(
    df: pd.DataFrame,
    columns: Iterable[str],
    salt: Optional[str] = None,
    copy: bool = True,
) -> pd.DataFrame:
    """
    Anonymize identifiers via hashing for safe sharing.

    Replaces identifier values with one-way cryptographic hashes,
    enabling re-identification within the dataset while obscuring
    the original values.

    Args:
        df (pd.DataFrame): Input DataFrame
        columns (Iterable[str]): Identifier columns to anonymize
        salt (str): Salt to add to hash for security. Default: None
        copy (bool): Return a copy or modify in-place. Default: True

    Returns:
        pd.DataFrame: DataFrame with anonymized identifiers

    Raises:
        TypeError: If input is not a DataFrame
        ValueError: If columns don't exist

    Example:
        >>> df = pd.DataFrame({'customer_id': ['CUST001', 'CUST002']})
        >>> anon = anonymize_identifiers(df, ['customer_id'], salt='secret')
        >>> # customer_id now contains hashes instead of original values
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    cols = list(columns)
    missing = [col for col in cols if col not in df.columns]
    if missing:
        raise ValueError(f"Columns not found: {missing}")

    if copy:
        df = df.copy()

    salt_str = salt or ""

    for col in cols:
        # Hash non-null values
        df[col] = df[col].apply(
            lambda x: (
                hashlib.sha256(f"{salt_str}{x}".encode()).hexdigest()[:16]
                if pd.notna(x)
                else None
            )
        )

    audit_log("anonymize_identifiers", before=None, after=df)
    return df
