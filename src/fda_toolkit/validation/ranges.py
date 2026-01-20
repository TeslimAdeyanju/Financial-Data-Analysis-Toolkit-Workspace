"""
Data range validation utilities.

This module provides functions to validate that values fall within
acceptable numeric and date ranges.
"""

from __future__ import annotations

from typing import Any, Dict, Tuple

import pandas as pd

from fda_toolkit.utils.logging import audit_log
from fda_toolkit.registry import register_function


@register_function(
    name="validate_data_ranges",
    category="Validation",
    module="validation.ranges",
)
def validate_data_ranges(
    df: pd.DataFrame,
    range_rules: Dict[str, Tuple[Any, Any]],
) -> pd.DataFrame:
    """
    Validate numeric and date ranges.

    Checks that values in specified columns fall within defined bounds.
    Returns a boolean DataFrame indicating violations per row.

    Args:
        df (pd.DataFrame): Input DataFrame
        range_rules (dict): Mapping of column to (min, max) bounds.
                           Example: {'amount': (0, 1_000_000), 'age': (0, 120)}

    Returns:
        pd.DataFrame: Boolean DataFrame indicating which values violate bounds

    Raises:
        TypeError: If input is not a DataFrame or range_rules is not dict
        ValueError: If column doesn't exist or bounds are invalid

    Example:
        >>> df = pd.DataFrame({'amount': [100, -50, 1500], 'age': [25, 35, 150]})
        >>> validate_data_ranges(
        ...     df, 
        ...     {'amount': (0, 1000), 'age': (0, 120)}
        ... )
        amount   age
        0   False  False
        1    True  False
        2    True   True
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    if not isinstance(range_rules, dict):
        raise TypeError("range_rules must be a dictionary")

    violations = pd.DataFrame(False, index=df.index, columns=range_rules.keys())

    for col, (min_val, max_val) in range_rules.items():
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found")

        if min_val > max_val:
            raise ValueError(f"Invalid bounds for '{col}': min > max")

        # Handle datetime columns
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            min_val = pd.to_datetime(min_val)
            max_val = pd.to_datetime(max_val)

        violations[col] = (df[col] < min_val) | (df[col] > max_val)

    audit_log("validate_data_ranges", before=None, after=violations)
    return violations
