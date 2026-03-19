from __future__ import annotations

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    import narwhals as nw
    import narwhals.typing


class StatIdentity:
    """Passthrough stat — returns data unchanged."""

    required_aes: frozenset[str] = frozenset()

    def compute(self, df: nw.typing.IntoFrame) -> nw.typing.Frame:
        import narwhals as nw

        return cast("nw.typing.Frame", nw.from_native(df))
