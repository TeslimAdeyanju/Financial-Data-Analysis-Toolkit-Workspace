from __future__ import annotations

from typing import Any, Dict

from fda_toolkit.pipelines.quick_clean import quick_clean, quick_clean_finance


def get_registry() -> Dict[str, Dict[str, Any]]:
    return {
        "quick_clean": {
            "callable": quick_clean,
            "category": "Convenience and One Line Utilities",
            "module": "pipelines.quick_clean",
            "description": "One line generic cleaning pipeline.",
        },
        "quick_clean_finance": {
            "callable": quick_clean_finance,
            "category": "Convenience and One Line Utilities",
            "module": "pipelines.quick_clean",
            "description": "One line finance cleaning pipeline.",
        },
    }
