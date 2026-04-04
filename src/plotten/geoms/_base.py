"""Base mixin for geom classes providing a useful __repr__."""

from __future__ import annotations


class GeomRepr:
    """Mixin that provides a descriptive __repr__ for geom classes.

    Attributes
    ----------
    warn_row_threshold : int or None
        If not None, a :class:`~plotten._validation.PlottenWarning` is
        emitted when the number of rows reaching ``draw()`` exceeds this
        value.  Aggregating geoms (histogram, density, boxplot, etc.)
        should set this to ``None`` since their stats reduce row counts.
    """

    warn_row_threshold: int | None = 100_000

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"
