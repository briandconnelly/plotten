"""Built-in labeller functions for faceted plots."""

from __future__ import annotations

import textwrap
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable


def label_value(label: str) -> str:
    """Display just the value (default behavior)."""
    return label


def label_both(label: str, *, sep: str = ": ") -> str:
    """Display 'variable: value' format.

    Note: Since plotten passes just the value string, this function
    needs to be created with the variable name bound. Use as:
        labeller=lambda v: label_both_with_var("species", v)
    Or use the factory below.
    """
    return label


def labeller_both(var: str, sep: str = ": ") -> Callable[[str], str]:
    """Create a labeller that shows 'variable: value'.

    Usage: facet_wrap("species", labeller=labeller_both("species"))
    """

    def _label(value: str) -> str:
        return f"{var}{sep}{value}"

    return _label


def labeller_wrap(width: int = 20) -> Callable[[str], str]:
    """Create a labeller that wraps long labels.

    Usage: facet_wrap("description", labeller=labeller_wrap(15))
    """

    def _label(value: str) -> str:
        return "\n".join(textwrap.wrap(value, width=width))

    return _label
