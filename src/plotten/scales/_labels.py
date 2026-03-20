from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable


def label_comma() -> Callable[[float], str]:
    """Format numbers with comma separators."""
    return lambda x: f"{x:,.0f}"


def label_percent(accuracy: float = 1, scale: float = 100) -> Callable[[float], str]:
    """Format numbers as percentages.

    Parameters
    ----------
    accuracy : float
        Number of decimal places.
    scale : float
        Multiplier applied before formatting.  Use ``100`` (default) when
        data is in 0-1 range (e.g. 0.5 -> "50.0%").  Use ``1`` when data
        is already in percent (e.g. 50 -> "50.0%").

    Examples
    --------
    >>> label_percent()(0.5)
    '50.0%'
    >>> label_percent(scale=1)(50)
    '50.0%'
    """
    decimals = int(accuracy)
    return lambda x: f"{x * scale:.{decimals}f}%"


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


def label_bytes(units: str = "auto", accuracy: int = 1) -> Callable[[float], str]:
    """Format numbers as byte sizes (KB, MB, GB, etc.).

    Parameters
    ----------
    units : str
        Fixed unit (``"B"``, ``"KB"``, ``"MB"``, ``"GB"``, ``"TB"``) or
        ``"auto"`` to pick based on magnitude.
    accuracy : int
        Number of decimal places.

    Examples
    --------
    >>> label_bytes()  # doctest: +SKIP
    >>> fmt = label_bytes()
    >>> fmt(1536)
    '1.5 KB'
    >>> fmt(2_500_000)
    '2.4 MB'
    """
    _units = ["B", "KB", "MB", "GB", "TB", "PB", "EB"]
    _fixed_exp: int | None = None
    if units != "auto":
        units_upper = units.upper()
        if units_upper in _units:
            _fixed_exp = _units.index(units_upper)

    def _fmt(x: float) -> str:
        if x == 0:
            return f"0 {_units[_fixed_exp or 0]}"
        if _fixed_exp is not None:
            val = x / (1024**_fixed_exp)
            return f"{val:.{accuracy}f} {_units[_fixed_exp]}"
        exp = min(int(math.log(abs(x), 1024)), len(_units) - 1)
        val = x / (1024**exp)
        return f"{val:.{accuracy}f} {_units[exp]}"

    return _fmt


def label_ordinal(big_mark: str = "") -> Callable[[float], str]:
    """Format numbers as ordinals (1st, 2nd, 3rd, ...).

    Parameters
    ----------
    big_mark : str
        Thousands separator (default: none).

    Examples
    --------
    >>> fmt = label_ordinal()
    >>> [fmt(i) for i in [1, 2, 3, 4, 11, 12, 13, 21, 22, 23]]
    ['1st', '2nd', '3rd', '4th', '11th', '12th', '13th', '21st', '22nd', '23rd']
    """

    def _fmt(x: float) -> str:
        n = int(x)
        if big_mark:
            n_str = f"{n:,}".replace(",", big_mark)
        else:
            n_str = str(n)
        if 11 <= abs(n) % 100 <= 13:
            return f"{n_str}th"
        remainder = abs(n) % 10
        if remainder == 1:
            return f"{n_str}st"
        if remainder == 2:
            return f"{n_str}nd"
        if remainder == 3:
            return f"{n_str}rd"
        return f"{n_str}th"

    return _fmt


def label_date(fmt: str = "%Y-%m-%d") -> Callable[[float], str]:
    """Format matplotlib date numbers as date strings.

    Parameters
    ----------
    fmt : str
        ``strftime`` format string.

    Examples
    --------
    >>> from plotten import scale_x_continuous
    >>> scale_x_continuous(labels=label_date("%b %Y"))  # doctest: +SKIP
    """
    import matplotlib.dates as mdates

    def _fmt(x: float) -> str:
        try:
            dt = mdates.num2date(x)
            return dt.strftime(fmt)
        except (ValueError, OverflowError):
            return str(x)

    return _fmt


def label_log(base: int = 10) -> Callable[[float], str]:
    """Format values as base^exponent (e.g. 10^2, 10^3).

    Parameters
    ----------
    base : int
        Logarithm base (default 10).

    Examples
    --------
    >>> fmt = label_log(10)
    >>> [fmt(v) for v in [1, 10, 100, 1000]]
    ['10⁰', '10¹', '10²', '10³']
    """
    _superscripts = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")

    def _fmt(x: float) -> str:
        if x <= 0:
            return str(x)
        exp = math.log(x, base)
        if abs(exp - round(exp)) < 1e-9:
            exp_str = str(round(exp)).translate(_superscripts)
            return f"{base}{exp_str}"
        return str(x)

    return _fmt


def label_si(accuracy: int = 1) -> Callable[[float], str]:
    """Format numbers with SI prefixes (k, M, G, T, ...).

    Uses base-1000 (not 1024).  For byte sizes use :func:`label_bytes`.

    Parameters
    ----------
    accuracy : int
        Number of decimal places.

    Examples
    --------
    >>> fmt = label_si()
    >>> [fmt(v) for v in [0, 1500, 2_500_000, 3_800_000_000]]
    ['0', '1.5k', '2.5M', '3.8G']
    """
    _prefixes = [
        (1e15, "P"),
        (1e12, "T"),
        (1e9, "G"),
        (1e6, "M"),
        (1e3, "k"),
    ]

    def _fmt(x: float) -> str:
        if x == 0:
            return "0"
        sign = "-" if x < 0 else ""
        ax = abs(x)
        for threshold, prefix in _prefixes:
            if ax >= threshold:
                return f"{sign}{ax / threshold:.{accuracy}f}{prefix}"
        # Below 1k — format as plain number
        if ax == int(ax):
            return f"{sign}{int(ax)}"
        return f"{sign}{ax:.{accuracy}f}"

    return _fmt


def label_pvalue(accuracy: int = 3, threshold: float = 0.001) -> Callable[[float], str]:
    """Format p-values with conventional scientific notation.

    Values below *threshold* are displayed as ``"< {threshold}"``.
    Values of 1.0 are shown as ``"1"``.

    Parameters
    ----------
    accuracy : int
        Decimal places for values above the threshold.
    threshold : float
        Values below this are shown as ``"< {threshold}"``.

    Examples
    --------
    >>> fmt = label_pvalue()
    >>> [fmt(v) for v in [0.85, 0.032, 0.0001]]
    ['0.850', '0.032', '< 0.001']
    """

    def _fmt(x: float) -> str:
        if x < 0:
            return str(x)
        if x >= 1:
            return "1"
        if x < threshold:
            return f"< {threshold}"
        return f"{x:.{accuracy}f}"

    return _fmt


def label_duration(accuracy: int = 0) -> Callable[[float], str]:
    """Format seconds as human-readable durations.

    Automatically picks the largest appropriate unit and includes
    up to two components (e.g. ``"2h 30m"``).

    Parameters
    ----------
    accuracy : int
        Decimal places for the smallest displayed unit.

    Examples
    --------
    >>> fmt = label_duration()
    >>> [fmt(v) for v in [45, 3661, 90061]]
    ['45s', '1h 1m', '1d 1h']
    """
    _units = [
        (86400, "d"),
        (3600, "h"),
        (60, "m"),
        (1, "s"),
    ]

    def _fmt(x: float) -> str:
        if x < 0:
            return f"-{_fmt(-x)}"
        if x == 0:
            return "0s"
        parts: list[str] = []
        remainder = float(x)
        for divisor, suffix in _units:
            if remainder >= divisor:
                count = int(remainder // divisor)
                remainder -= count * divisor
                parts.append(f"{count}{suffix}")
                if len(parts) == 2:
                    break
        if not parts:
            # Sub-second
            if accuracy > 0:
                return f"{x:.{accuracy}f}s"
            return f"{x:.1f}s"
        return " ".join(parts)

    return _fmt


def label_currency(
    prefix: str = "$",
    suffix: str = "",
    accuracy: int = 2,
    big_mark: str = ",",
) -> Callable[[float], str]:
    """Format numbers as currency with configurable prefix, suffix, and precision.

    A generalized version of :func:`label_dollar` supporting any currency
    symbol, suffix-style currencies, and configurable decimal places.

    Parameters
    ----------
    prefix : str
        Currency symbol placed before the number (default ``"$"``).
    suffix : str
        Currency symbol placed after the number (default ``""``).
    accuracy : int
        Number of decimal places (default 2).
    big_mark : str
        Thousands separator (default ``","``).

    Examples
    --------
    >>> label_currency()  # same as label_dollar
    >>> fmt = label_currency(prefix="EUR ", accuracy=2)
    >>> fmt(1234.5)
    'EUR 1,234.50'
    >>> fmt2 = label_currency(prefix="", suffix=" kr", accuracy=0)
    >>> fmt2(9500)
    '9,500 kr'
    """

    def _fmt(x: float) -> str:
        negative = x < 0
        ax = abs(x)
        formatted = f"{ax:,.{accuracy}f}"
        if big_mark != ",":
            formatted = formatted.replace(",", big_mark)
        result = f"{prefix}{formatted}{suffix}"
        if negative:
            result = f"-{result}"
        return result

    return _fmt


def label_date_short() -> Callable[[float], str]:
    """Format matplotlib date numbers with auto-abbreviated labels.

    Automatically picks the format based on the value's resolution:

    * Times within a single day: ``"HH:MM"``
    * Days within a single month: ``"Mon DD"``  (e.g. ``"Jan 15"``)
    * Months within a single year: ``"Mon"``  (e.g. ``"Jan"``)
    * Otherwise: ``"Mon YYYY"``  (e.g. ``"Jan 2024"``)

    Unlike :func:`label_date`, no format string is needed -- the formatter
    adapts to whatever tick spacing the scale produces.

    Examples
    --------
    >>> from plotten import scale_x_continuous
    >>> scale_x_continuous(labels=label_date_short())  # doctest: +SKIP
    """
    import matplotlib.dates as mdates

    def _fmt(x: float) -> str:
        try:
            dt = mdates.num2date(x)
        except (ValueError, OverflowError):
            return str(x)
        # Check fractional day (sub-day precision)
        if x != int(x):
            return dt.strftime("%H:%M")
        # Day-level: show "Jan 15" style
        if dt.day != 1:
            return dt.strftime("%b %d").lstrip("0")
        # Month boundaries: show "Jan" for mid-year, "Jan 2024" for Jan
        if dt.month == 1:
            return dt.strftime("%b %Y")
        return dt.strftime("%b")

    return _fmt


def label_number_auto() -> Callable[[float], str]:
    """Automatically format numbers based on magnitude.

    Picks the most readable format for each value:

    * Very large (>= 1e6): SI prefixes (``"2.5M"``)
    * Large (>= 1000): comma separators (``"12,500"``)
    * Small integers: plain (``"42"``)
    * Small decimals: up to 2 decimal places (``"3.14"``)
    * Very small (< 0.01): scientific notation (``"5.00e-04"``)

    This is the "just make it look good" formatter -- useful as a
    default when you don't want to think about formatting.

    Examples
    --------
    >>> fmt = label_number_auto()
    >>> [fmt(v) for v in [0.005, 3.14, 42, 12500, 2_500_000]]
    ['5.00e-03', '3.14', '42', '12,500', '2.5M']
    """
    _si_prefixes = [
        (1e15, "P"),
        (1e12, "T"),
        (1e9, "G"),
        (1e6, "M"),
    ]

    def _fmt(x: float) -> str:
        if x == 0:
            return "0"
        ax = abs(x)
        sign = "-" if x < 0 else ""
        # Very large: SI prefixes
        for threshold, prefix in _si_prefixes:
            if ax >= threshold:
                return f"{sign}{ax / threshold:.1f}{prefix}"
        # Large: comma separators
        if ax >= 1000:
            return f"{x:,.0f}"
        # Integers
        if ax >= 1 and ax == int(ax):
            return f"{sign}{int(ax)}"
        # Normal decimals
        if ax >= 0.01:
            # Strip trailing zeros but keep at least one decimal
            formatted = f"{x:.2f}".rstrip("0").rstrip(".")
            return formatted
        # Very small: scientific
        return f"{x:.2e}"

    return _fmt


def label_wrap(width: int = 20) -> Callable:
    """Wrap long label text across multiple lines.

    Useful for long categorical labels on axes.

    Parameters
    ----------
    width : int
        Maximum characters per line before wrapping.

    Examples
    --------
    >>> fmt = label_wrap(10)
    >>> fmt("A very long category name")
    'A very\\nlong\\ncategory\\nname'
    """
    import textwrap

    def _fmt(x: object) -> str:
        return textwrap.fill(str(x), width=width)

    return _fmt
