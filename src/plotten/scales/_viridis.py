"""Viridis family convenience scales."""

from __future__ import annotations

from plotten.scales._color import ScaleColorContinuous

# Map ggplot2-style letter codes and names to matplotlib cmap names
_VIRIDIS_OPTIONS: dict[str, str] = {
    "viridis": "viridis",
    "magma": "magma",
    "inferno": "inferno",
    "plasma": "plasma",
    "cividis": "cividis",
    "A": "magma",
    "B": "inferno",
    "C": "plasma",
    "D": "viridis",
    "E": "cividis",
}


def _resolve_option(option: str) -> str:
    if option in _VIRIDIS_OPTIONS:
        return _VIRIDIS_OPTIONS[option]
    msg = (
        f"Unknown viridis option: {option!r}. "
        f"Valid options: {sorted(k for k in _VIRIDIS_OPTIONS if len(k) > 1)}"
    )
    raise ValueError(msg)


def scale_color_viridis(option: str = "viridis", **kwargs) -> ScaleColorContinuous:
    """Create a continuous color scale using a viridis-family palette."""
    return ScaleColorContinuous(aesthetic="color", cmap_name=_resolve_option(option), **kwargs)


def scale_fill_viridis(option: str = "viridis", **kwargs) -> ScaleColorContinuous:
    """Create a continuous fill scale using a viridis-family palette."""
    return ScaleColorContinuous(aesthetic="fill", cmap_name=_resolve_option(option), **kwargs)
