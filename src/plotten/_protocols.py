from __future__ import annotations
from typing import Protocol, Any, runtime_checkable


@runtime_checkable
class Stat(Protocol):
    required_aes: frozenset[str]

    def compute(self, df: Any) -> Any:
        """Takes a narwhals df, returns a narwhals df."""
        ...


@runtime_checkable
class Geom(Protocol):
    required_aes: frozenset[str]
    default_stat: type[Stat]

    def draw(self, data: Any, ax: Any, params: dict) -> None: ...


@runtime_checkable
class Scale(Protocol):
    aesthetic: str

    def train(self, data: Any) -> None: ...
    def map_data(self, values: Any) -> Any: ...
    def get_limits(self) -> tuple: ...
    def get_breaks(self) -> list: ...


@runtime_checkable
class Coord(Protocol):
    def transform(self, data: Any, ax: Any) -> Any: ...


@runtime_checkable
class Facet(Protocol):
    def facet_data(self, data: Any) -> list: ...


@runtime_checkable
class Position(Protocol):
    def adjust(self, data: Any) -> Any: ...
