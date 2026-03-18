from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True, kw_only=True)
class GuideLegend:
    """Customization for discrete legends."""

    title: str | None = None
    nrow: int | None = None
    ncol: int | None = None
    reverse: bool = False
    override_aes: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class GuideColorbar:
    """Customization for continuous colorbar legends."""

    title: str | None = None
    barwidth: float | None = None
    barheight: float | None = None
    nbin: int = 256
    reverse: bool = False


def guide_legend(**kwargs: Any) -> GuideLegend:
    return GuideLegend(**kwargs)


def guide_colorbar(**kwargs: Any) -> GuideColorbar:
    return GuideColorbar(**kwargs)


def guides(**kwargs: Any) -> dict[str, GuideLegend | GuideColorbar]:
    """Map aesthetic names to guide specs.

    Example: ``guides(color=guide_legend(title="Species"))``
    """
    return dict(kwargs)
