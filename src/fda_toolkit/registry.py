"""Central registry for dynamic discovery of functions.

The @register_function decorator is used on all functions to auto-register them.
This enables dynamic discovery and automated function listing without manual updates.

Example:
    @register_function(
        name="clean_headers",
        category="Data Cleaning",
        module="core.columns"
    )
    def clean_column_headers(df):
        ...
"""

from __future__ import annotations

from typing import Any, Dict, Callable


# Global function registry
FUNCTION_REGISTRY: Dict[str, Dict[str, Any]] = {}


def register_function(
    name: str,
    category: str,
    module: str,
) -> Callable:
    """
    Decorator to register a function in the global registry.

    Args:
        name (str): Display name for the function
        category (str): Functional category (e.g., 'Data Cleaning', 'Validation')
        module (str): Module path (e.g., 'core.columns')

    Returns:
        Callable: Decorator function

    Example:
        >>> @register_function(name="my_func", category="Utilities", module="utils.my_module")
        ... def my_func(df):
        ...     pass
    """

    def decorator(func: Callable) -> Callable:
        FUNCTION_REGISTRY[name] = {
            "callable": func,
            "category": category,
            "module": module,
            "doc": func.__doc__,
            "name": name,
        }
        return func

    return decorator


def get_combined_registry() -> Dict[str, Dict[str, Any]]:
    """
    Get the combined registry of all registered functions.

    Returns:
        dict: Global function registry

    Example:
        >>> registry = get_combined_registry()
        >>> len(registry)
        50
    """
    return FUNCTION_REGISTRY.copy()
