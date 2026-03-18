from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable


def label_comma() -> Callable[[float], str]:
    """Format numbers with comma separators."""
    return lambda x: f"{x:,.0f}"


def label_percent(accuracy: float = 1) -> Callable[[float], str]:
    """Format numbers as percentages."""
    decimals = int(accuracy)
    return lambda x: f"{x * 100:.{decimals}f}%"


def label_dollar(prefix: str = "$") -> Callable[[float], str]:
    """Format numbers as currency."""
    return lambda x: f"{prefix}{x:,.2f}"


def label_scientific() -> Callable[[float], str]:
    """Format numbers in scientific notation."""
    return lambda x: f"{x:.2e}"


def label_number(accuracy: int = 0, big_mark: str = ",") -> Callable[[float], str]:
    """Format numbers with configurable precision and thousands separator."""

    def _fmt(x: float) -> str:
        if accuracy > 0:
            formatted = f"{x:.{accuracy}f}"
        else:
            formatted = f"{x:.0f}"
        if big_mark == ",":
            # Use locale-style formatting
            parts = formatted.split(".")
            int_part = parts[0]
            # Add thousands separator
            negative = int_part.startswith("-")
            if negative:
                int_part = int_part[1:]
            groups = []
            while len(int_part) > 3:
                groups.append(int_part[-3:])
                int_part = int_part[:-3]
            groups.append(int_part)
            int_part = big_mark.join(reversed(groups))
            if negative:
                int_part = "-" + int_part
            if len(parts) > 1:
                return f"{int_part}.{parts[1]}"
            return int_part
        return formatted

    return _fmt
