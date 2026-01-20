from __future__ import annotations

from typing import Any, Callable, Dict

import pandas as pd


def validate_business_rules(
    df: pd.DataFrame,
    rules: Dict[str, Callable[[pd.DataFrame], pd.Series]],
) -> pd.DataFrame:
    """Validate custom business rules.

    rules maps rule_name to a function returning a boolean mask where True means violation.
    """

    raise NotImplementedError("validate_business_rules is not implemented yet")
