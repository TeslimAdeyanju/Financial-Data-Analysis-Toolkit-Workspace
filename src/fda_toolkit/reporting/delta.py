"""
Data change tracking and comparison utilities.

This module provides functions to track changes between data snapshots
and generate delta reports for reconciliation.
"""

from __future__ import annotations

from typing import Dict, Optional
import hashlib

import pandas as pd

from fda_toolkit.utils.logging import audit_log
from fda_toolkit.registry import register_function


@register_function(
    name="snapshot_dataset",
    category="Reporting",
    module="reporting.delta",
)
def snapshot_dataset(
    df: pd.DataFrame,
    key_cols: Optional[list[str]] = None,
) -> Dict[str, object]:
    """
    Create a snapshot containing row counts and basic hashes.

    Takes a point-in-time snapshot of a dataset for later comparison.
    Useful for tracking data changes across transformations.

    Args:
        df (pd.DataFrame): Input DataFrame
        key_cols (list[str]): Columns to use for row hashing. Default: all columns

    Returns:
        dict: Snapshot dictionary containing metadata and row hashes

    Raises:
        TypeError: If input is not a DataFrame

    Example:
        >>> df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
        >>> snap = snapshot_dataset(df)
        >>> snap['total_rows']
        2
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    snapshot = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "columns": df.columns.tolist(),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "shape": df.shape,
    }

    # Create row hashes for comparison
    if key_cols:
        subset = df[key_cols]
    else:
        subset = df

    row_hashes = subset.apply(
        lambda row: hashlib.md5(str(row.values).encode()).hexdigest(), axis=1
    ).tolist()

    snapshot["row_hashes"] = row_hashes
    snapshot["dataset_hash"] = hashlib.md5(
        "".join(row_hashes).encode()
    ).hexdigest()

    audit_log("snapshot_dataset", before=None, after=snapshot)
    return snapshot


@register_function(
    name="compare_snapshots",
    category="Reporting",
    module="reporting.delta",
)
def compare_snapshots(
    before: Dict[str, object],
    after: Dict[str, object],
) -> Dict[str, object]:
    """
    Compare snapshots and return differences.

    Identifies structural and content changes between two snapshots.

    Args:
        before (dict): Snapshot from before transformation
        after (dict): Snapshot from after transformation

    Returns:
        dict: Comparison report with changes

    Raises:
        TypeError: If inputs are not dictionaries

    Example:
        >>> snap1 = snapshot_dataset(df1)
        >>> snap2 = snapshot_dataset(df2)
        >>> comparison = compare_snapshots(snap1, snap2)
        >>> comparison['row_change']
        -5
    """
    if not isinstance(before, dict) or not isinstance(after, dict):
        raise TypeError("Both snapshots must be dictionaries")

    comparison = {
        "row_change": after.get("total_rows", 0) - before.get("total_rows", 0),
        "column_change": after.get("total_columns", 0) - before.get("total_columns", 0),
        "before_shape": before.get("shape"),
        "after_shape": after.get("shape"),
        "columns_added": [
            col for col in after.get("columns", []) if col not in before.get("columns", [])
        ],
        "columns_removed": [
            col for col in before.get("columns", []) if col not in after.get("columns", [])
        ],
        "dataset_hash_changed": (
            before.get("dataset_hash") != after.get("dataset_hash")
        ),
    }

    audit_log("compare_snapshots", before=None, after=comparison)
    return comparison


@register_function(
    name="delta_report",
    category="Reporting",
    module="reporting.delta",
)
def delta_report(
    before: pd.DataFrame,
    after: pd.DataFrame,
    key_col: str,
) -> Dict[str, object]:
    """
    Return added, removed, and changed keys.

    Compares two versions of a dataset and identifies which rows
    were added, removed, or modified based on a key column.

    Args:
        before (pd.DataFrame): DataFrame before transformation
        after (pd.DataFrame): DataFrame after transformation
        key_col (str): Column to use as unique identifier

    Returns:
        dict: Report with added, removed, and potentially changed rows

    Raises:
        TypeError: If inputs are not DataFrames
        ValueError: If key_col doesn't exist in both DataFrames

    Example:
        >>> before = pd.DataFrame({'id': [1, 2, 3], 'val': [10, 20, 30]})
        >>> after = pd.DataFrame({'id': [1, 2, 4], 'val': [10, 25, 40]})
        >>> delta = delta_report(before, after, 'id')
        >>> delta['added']
        [4]
    """
    if not isinstance(before, pd.DataFrame) or not isinstance(after, pd.DataFrame):
        raise TypeError("Both inputs must be DataFrames")

    if key_col not in before.columns or key_col not in after.columns:
        raise ValueError(f"Column '{key_col}' not found in both DataFrames")

    before_keys = set(before[key_col].dropna())
    after_keys = set(after[key_col].dropna())

    added = list(after_keys - before_keys)
    removed = list(before_keys - after_keys)
    unchanged = list(before_keys & after_keys)

    # Detect changed rows
    changed = []
    for key in unchanged:
        before_row = before[before[key_col] == key].iloc[0]
        after_row = after[after[key_col] == key].iloc[0]
        if not before_row.equals(after_row):
            changed.append(key)

    report = {
        "total_added": len(added),
        "total_removed": len(removed),
        "total_changed": len(changed),
        "total_unchanged": len(unchanged) - len(changed),
        "added_keys": added,
        "removed_keys": removed,
        "changed_keys": changed,
    }

    audit_log("delta_report", before=None, after=report)
    return report
