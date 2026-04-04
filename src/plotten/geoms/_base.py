"""Base mixin for geom classes providing a useful __repr__."""

from __future__ import annotations


class GeomRepr:
    """Mixin that provides a descriptive __repr__ for geom classes."""

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"
