from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    import narwhals as nw
    import narwhals.typing
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams


@runtime_checkable
class Stat(Protocol):
    required_aes: frozenset[str]

    def compute(self, df: nw.typing.IntoFrame) -> nw.typing.Frame:
        """Takes a narwhals-compatible frame, returns a narwhals frame."""
        ...


@runtime_checkable
class Geom(Protocol):
    required_aes: frozenset[str]
    supports_group_splitting: bool
    legend_key: str
    known_params: frozenset[str]

    def default_stat(self) -> Stat: ...
    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None: ...


@runtime_checkable
class Scale(Protocol):
    aesthetic: str

    def train(self, data: Any) -> None: ...
    def map_data(self, values: Any) -> Any: ...
    def get_limits(self) -> tuple: ...
    def get_breaks(self) -> list: ...


@runtime_checkable
class Coord(Protocol):
    def transform(self, data: Any, ax: Axes) -> Any: ...


@runtime_checkable
class Facet(Protocol):
    def facet_data(self, data: Any) -> list: ...


@runtime_checkable
class Position(Protocol):
    def adjust(self, data: Any, params: dict) -> Any: ...
