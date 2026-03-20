"""Stat that deduplicates observations."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    import narwhals as nw
    import narwhals.typing


class StatUnique:
    """Remove duplicate observations before plotting."""

    required_aes: frozenset[str] = frozenset()

    def compute(self, df: nw.typing.IntoFrame) -> nw.typing.Frame:
        import narwhals as nw

        frame = nw.from_native(df)
        return cast("nw.typing.Frame", frame.unique())
