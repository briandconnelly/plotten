"""Convenience function for saving plots."""

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
    units: str = "in",
    dpi: int = 300,
    transparent: bool = False,
) -> None:
    """Save a plot to a file.

    Parameters
    ----------
    plot : Plot
        The plot to save.
    filename : str or Path
        Path to the output file. The format is inferred from the extension.
    width, height : float, optional
        Dimensions of the output. If only one is given, the other is calculated
        from the figure's aspect ratio.
    units : str
        Unit for width/height: "in", "cm", "mm", or "px".
    dpi : int
        Resolution in dots per inch. Default 300 (publication quality).
    transparent : bool
        If True, the figure and axes backgrounds are transparent.
    """
    from plotten._render._mpl import render

    fig = render(plot)

    # Convert units to inches
    unit = SizeUnit(units)
    factors = {
        SizeUnit.INCHES: 1.0,
        SizeUnit.CM: 1 / 2.54,
        SizeUnit.MM: 1 / 25.4,
        SizeUnit.PX: 1 / dpi,
    }
    factor = factors[unit]

    # Handle dimensions
    orig_w, orig_h = fig.get_size_inches()
    aspect = orig_w / orig_h

    if width is not None and height is not None:
        new_w = width * factor
        new_h = height * factor
    elif width is not None:
        new_w = width * factor
        new_h = new_w / aspect
    elif height is not None:
        new_h = height * factor
        new_w = new_h * aspect
    else:
        new_w, new_h = orig_w, orig_h

    fig.set_size_inches(new_w, new_h)

    if transparent:
        fig.patch.set_alpha(0.0)
        for ax in fig.get_axes():
            ax.patch.set_alpha(0.0)

    import matplotlib.pyplot as plt

    fig.savefig(filename, dpi=dpi, bbox_inches="tight", transparent=transparent)
    plt.close(fig)
