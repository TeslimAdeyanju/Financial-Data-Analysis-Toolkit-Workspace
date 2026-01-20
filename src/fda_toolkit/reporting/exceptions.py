from __future__ import annotations

from typing import Dict, Optional

import pandas as pd


def exception_report(
    issues: pd.DataFrame,
    context: Optional[Dict[str, str]] = None,
) -> Dict[str, object]:
    """Create an exception report object for logging and export."""

    raise NotImplementedError("exception_report is not implemented yet")
