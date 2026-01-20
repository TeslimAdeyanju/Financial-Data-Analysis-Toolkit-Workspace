"""
Data type optimization utilities.

This module provides functions to optimize memory usage by downcasting
data types safely.
"""

from __future__ import annotations

from typing import Optional

import pandas as pd
import numpy as np

from fda_toolkit.utils.logging import audit_log
from fda_toolkit.registry import register_function


@register_function(
    name="optimize_dtypes",
    category="Utilities",
    module="utils.types",
)
def optimize_dtypes(df: pd.DataFrame, copy: bool = True) -> pd.DataFrame:
    """
    Downcast numeric dtypes where safe to reduce memory usage.

    Intelligently converts columns to the smallest appropriate dtype:
    - int64 → int32/int16/int8 where values fit
    - float64 → float32 where precision permits
    - object → category for columns with low cardinality

    Args:
        df (pd.DataFrame): Input DataFrame
        copy (bool): Return a copy or modify in-place. Default: True

    Returns:
        pd.DataFrame: DataFrame with optimized dtypes

    Raises:
        TypeError: If input is not a DataFrame

    Example:
        >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': ['cat', 'dog', 'cat']})
        >>> optimized = optimize_dtypes(df)
        >>> optimized['A'].dtype
        dtype('int8')  # Downcasted from int64
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    if copy:
        df = df.copy()

    before_memory = df.memory_usage(deep=True).sum()

    for col in df.columns:
        col_type = df[col].dtype

        # Skip if already optimized or not applicable
        if col_type == "object":
            # Try to convert to category if cardinality is low
            num_unique = df[col].nunique()
            total = len(df)
            if num_unique / total < 0.05:  # < 5% cardinality
                df[col] = df[col].astype("category")

        elif col_type == "int64":
            # Downcast integers
            col_min = df[col].min()
            col_max = df[col].max()

            if col_min >= 0:
                if col_max < 256:
                    df[col] = df[col].astype("uint8")
                elif col_max < 65536:
                    df[col] = df[col].astype("uint16")
                elif col_max < 4294967296:
                    df[col] = df[col].astype("uint32")
            else:
                if col_min > -128 and col_max < 127:
                    df[col] = df[col].astype("int8")
                elif col_min > -32768 and col_max < 32767:
                    df[col] = df[col].astype("int16")
                elif col_min > -2147483648 and col_max < 2147483647:
                    df[col] = df[col].astype("int32")

        elif col_type == "float64":
            # Try float32 if no significant precision loss
            try:
                converted = df[col].astype("float32")
                # Check if conversion loses data
                if not np.allclose(df[col], converted, rtol=1e-6, equal_nan=True):
                    continue
                df[col] = converted
            except (ValueError, TypeError):
                pass

    after_memory = df.memory_usage(deep=True).sum()
    reduction_pct = ((before_memory - after_memory) / before_memory) * 100

    audit_log(
        "optimize_dtypes",
        before=f"{before_memory / 1024**2:.2f} MB",
        after=f"{after_memory / 1024**2:.2f} MB ({reduction_pct:.1f}% reduction)",
    )

    return df
