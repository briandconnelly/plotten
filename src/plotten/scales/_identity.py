"""Identity scales — use data values directly as aesthetic values."""

from __future__ import annotations

from typing import Any

import narwhals as nw

from plotten.scales._base import ScaleBase


class ScaleIdentity(ScaleBase):
    """Use data values directly as aesthetic values, with no transformation."""

    def __init__(self, aesthetic: str, guide: str = "none") -> None:
        super().__init__(aesthetic)
        self._guide = guide

    def train(self, values: Any) -> None:
        s = nw.from_native(values, series_only=True)
        levels = s.unique().sort().to_list()
        if self._domain_min is None:
            self._levels: list = []
        for lev in levels:
            if lev not in self._levels:
                self._levels.append(lev)

    def map_data(self, values: Any) -> Any:
        # Identity: return data as-is (no transformation)
        return values

    def get_limits(self) -> tuple[float, float]:
        return (0, max(len(self._levels) - 1, 1))

    def get_breaks(self) -> list:
        return list(range(len(self._levels)))

    def get_labels(self) -> list[str]:
        return [str(v) for v in self._levels]

    def legend_entries(self) -> list | None:
        if self._guide == "none":
            return None
        return None


def scale_color_identity(guide: str = "none") -> ScaleIdentity:
    return ScaleIdentity("color", guide=guide)


def scale_fill_identity(guide: str = "none") -> ScaleIdentity:
    return ScaleIdentity("fill", guide=guide)


def scale_alpha_identity(guide: str = "none") -> ScaleIdentity:
    return ScaleIdentity("alpha", guide=guide)


def scale_size_identity(guide: str = "none") -> ScaleIdentity:
    return ScaleIdentity("size", guide=guide)


def scale_shape_identity(guide: str = "none") -> ScaleIdentity:
    return ScaleIdentity("shape", guide=guide)


def scale_linetype_identity(guide: str = "none") -> ScaleIdentity:
    return ScaleIdentity("linetype", guide=guide)
