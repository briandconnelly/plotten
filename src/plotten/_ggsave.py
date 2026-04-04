"""Convenience function for saving plots (deprecated)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

from plotten._enums import SizeUnit


def ggsave(
    plot: Any,
    filename: str | Path,
    *,
    width: float | None = None,
    height: float | None = None,
    units: str | SizeUnit = SizeUnit.INCHES,
    dpi: int = 300,
    transparent: bool = False,
) -> None:
    """Save a plot to a file.

    .. deprecated::
        Use :meth:`Plot.save` instead::

            plot.save("output.png", dpi=300)

    Parameters
    ----------
    plot : Plot
        The plot to save.
    filename : str or Path
        Path to the output file. The format is inferred from the extension.
    width, height : float, optional
        Dimensions of the output. If only one is given, the other is calculated
        from the figure's aspect ratio.
    units : str or SizeUnit
        Unit for width/height: ``SizeUnit.INCHES`` (default), ``SizeUnit.CM``,
        ``SizeUnit.MM``, or ``SizeUnit.PX``. Plain strings are also accepted.
    dpi : int
        Resolution in dots per inch. Default 300 (publication quality).
    transparent : bool
        If True, the figure and axes backgrounds are transparent.
    """
    from plotten._validation import plotten_deprecation_warn

    plotten_deprecation_warn(
        "ggsave() is deprecated. Use plot.save() instead: plot.save('output.png', dpi=300)"
    )
    plot.save(
        str(filename),
        dpi=dpi,
        width=width,
        height=height,
        units=units,
        transparent=transparent,
    )
