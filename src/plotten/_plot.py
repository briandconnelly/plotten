from __future__ import annotations

import io
from dataclasses import dataclass, field
from typing import Any, Self

from plotten._aes import Aes
from plotten._enums import SizeUnit
from plotten._guides import Guides
from plotten._labs import Labs
from plotten._layer import Layer
from plotten._watermark import Watermark
from plotten.coords._cartesian import CoordCartesian
from plotten.coords._equal import CoordEqual, CoordFixed
from plotten.coords._flip import CoordFlip
from plotten.coords._polar import CoordPolar
from plotten.coords._trans import CoordTrans
from plotten.facets import FacetGrid, FacetWrap
from plotten.scales._base import ScaleBase
from plotten.themes._theme import Theme


@dataclass(frozen=True, slots=True)
class Plot:
    """Immutable plot specification built up via ``+`` operator."""

    data: Any = None
    mapping: Aes = field(default_factory=Aes)
    layers: tuple[Layer, ...] = ()
    scales: tuple[ScaleBase, ...] = ()
    coord: Any = field(default_factory=CoordCartesian)
    theme: Theme = field(default_factory=Theme)
    labs: Labs = field(default_factory=Labs)
    facet: Any = None
    guides: Guides | None = None
    _expand_limits: tuple = ()
    _insets: tuple = ()
    _watermark: Watermark | None = None

    def __repr__(self) -> str:
        parts = [f"layers={len(self.layers)}"]
        if self.facet is not None:
            parts.append(f"facet={type(self.facet).__name__}")
        if self.theme.complete:
            parts.append("theme=<complete>")
        coord_name = type(self.coord).__name__
        if coord_name != "CoordCartesian":
            parts.append(f"coord={coord_name}")
        return f"Plot({', '.join(parts)})"

    def _replace(self, **kwargs: Any) -> Self:
        """Return a copy with given fields replaced."""
        from dataclasses import fields as dc_fields

        vals = {f.name: getattr(self, f.name) for f in dc_fields(self)}
        vals.update(kwargs)
        return type(self)(**vals)

    def __add__(self, other: Any) -> Plot:
        from plotten._expand_limits import ExpandLimits

        match other:
            case Layer():
                return self._replace(layers=(*self.layers, other))
            case ScaleBase():
                return self._replace(scales=(*self.scales, other))
            case Theme():
                return self._replace(theme=self.theme + other)
            case Labs():
                return self._replace(labs=self.labs + other)
            case (
                CoordCartesian()
                | CoordFlip()
                | CoordEqual()
                | CoordFixed()
                | CoordPolar()
                | CoordTrans()
            ):
                return self._replace(coord=other)
            case FacetWrap() | FacetGrid():
                return self._replace(facet=other)
            case ExpandLimits():
                return self._replace(_expand_limits=(*self._expand_limits, other))
            case Watermark():
                return self._replace(_watermark=other)
            case Guides():
                existing = self.guides or Guides()
                return self._replace(guides=Guides({**existing, **other}))
            case _:
                from plotten._composition import InsetElement

                if isinstance(other, InsetElement):
                    return self._replace(_insets=(*self._insets, other))

                from plotten._validation import ConfigError

                raise ConfigError(
                    f"Cannot add {type(other).__name__!r} to a Plot. "
                    f"Use layers (geom_*), scales (scale_*), themes (theme), "
                    f"labels (labs), coords (coord_*), facets (facet_*), or guides."
                )

    def __or__(self, other: Any) -> Any:
        from plotten._composition import PlotGrid

        if isinstance(other, Plot | PlotGrid):
            return PlotGrid(plots=(self, other), direction="h")
        return NotImplemented

    def __truediv__(self, other: Any) -> Any:
        from plotten._composition import PlotGrid

        if isinstance(other, Plot | PlotGrid):
            return PlotGrid(plots=(self, other), direction="v")
        return NotImplemented

    def show(self) -> None:
        """Render and display the plot."""
        from plotten._render._mpl import render

        fig = render(self)
        fig.show()

    def save(
        self,
        path: str,
        dpi: int = 300,
        width: float | None = None,
        height: float | None = None,
        units: str | SizeUnit = SizeUnit.INCHES,
        transparent: bool = False,
    ) -> None:
        """Render and save the plot to a file.

        Parameters
        ----------
        path : str
            Output file path. Format is inferred from the extension
            (e.g. ``"plot.png"``, ``"plot.pdf"``).
        dpi : int, optional
            Resolution in dots per inch (default 300).
        width, height : float, optional
            Figure dimensions in *units*. If omitted, matplotlib defaults
            are used.
        units : str or SizeUnit, optional
            Units for *width* / *height*: ``SizeUnit.INCHES`` (default),
            ``SizeUnit.CM``, ``SizeUnit.MM``, or ``SizeUnit.PX``.
            Plain strings like ``"in"`` are also accepted.
        transparent : bool, optional
            If True, the figure and axes backgrounds are transparent
            (default False).

        Examples
        --------
        >>> import pandas as pd
        >>> from plotten import ggplot, aes, geom_point
        >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
        >>> p = ggplot(df, aes(x="x", y="y")) + geom_point()
        >>> p.save("scatter.png", dpi=300, width=6, height=4)  # doctest: +SKIP
        """
        from plotten._render._mpl import render

        fig = render(self)
        if width is not None or height is not None:
            match units:
                case SizeUnit.INCHES:
                    factor = 1.0
                case SizeUnit.CM:
                    factor = 1 / 2.54
                case SizeUnit.MM:
                    factor = 1 / 25.4
                case SizeUnit.PX:
                    factor = 1 / dpi
                case _:
                    factor = 1.0
            cur_w, cur_h = fig.get_size_inches()
            aspect = cur_w / cur_h
            if width is not None and height is not None:
                new_w = width * factor
                new_h = height * factor
            elif width is not None:
                new_w = width * factor
                new_h = new_w / aspect
            else:
                # width is None, height must be not None (guarded by outer if)
                new_h = height * factor  # type: ignore[operator]
                new_w = new_h * aspect
            fig.set_size_inches(new_w, new_h)
        if transparent:
            fig.patch.set_alpha(0.0)
            for ax in fig.get_axes():
                ax.patch.set_alpha(0.0)

        fig.savefig(path, dpi=dpi, transparent=transparent)
        import matplotlib.pyplot as plt

        plt.close(fig)

    def _repr_png_(self) -> bytes:
        """Jupyter integration — display as PNG."""
        from plotten._render._mpl import render

        fig = render(self)
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=150)
        import matplotlib.pyplot as plt

        plt.close(fig)
        return buf.getvalue()

    def _repr_html_(self) -> str | None:
        """Jupyter integration — interactive Vega-Lite display.

        Falls back to PNG (via ``_repr_png_``) if Vega-Lite conversion fails.
        """
        try:
            from plotten._vegalite import to_html

            return to_html(self)
        except ImportError:
            return None
        except Exception:
            import logging

            logging.getLogger("plotten").debug(
                "Vega-Lite conversion failed, falling back to PNG", exc_info=True
            )
            return None

    def _repr_mimebundle_(
        self, *, include: set[str] | None = None, exclude: set[str] | None = None
    ) -> dict[str, Any]:
        """Jupyter MIME bundle — let the frontend pick the best format.

        Provides ``text/html`` (interactive Vega-Lite) and ``image/png``
        so that JupyterLab picks HTML while classic Notebook can fall back
        to PNG.
        """
        bundle: dict[str, Any] = {}
        wanted = include or {"text/html", "image/png"}
        if exclude:
            wanted -= exclude

        if "text/html" in wanted:
            html = self._repr_html_()
            if html is not None:
                bundle["text/html"] = html

        if "image/png" in wanted:
            bundle["image/png"] = self._repr_png_()

        return bundle

    def _mime_(self) -> tuple[str, str]:
        """Marimo reactive notebook display protocol.

        Returns ``("text/html", html_string)`` for interactive Vega-Lite
        rendering, or a PNG data-URI fallback.
        """
        import base64

        try:
            from plotten._vegalite import to_html

            return ("text/html", to_html(self))
        except ImportError:
            png_bytes = self._repr_png_()
        except Exception:
            import logging

            logging.getLogger("plotten").debug(
                "Vega-Lite conversion failed, falling back to PNG", exc_info=True
            )
            png_bytes = self._repr_png_()

        data_uri = base64.b64encode(png_bytes).decode("ascii")
        return ("text/html", f'<img src="data:image/png;base64,{data_uri}" />')


def ggplot(data: Any = None, mapping: Aes | None = None) -> Plot:
    """Create a new plot.

    Parameters
    ----------
    data : DataFrame, optional
        Default dataset for the plot. Any DataFrame supported by narwhals
        (pandas, Polars, cuDF, etc.).
    mapping : Aes, optional
        Default aesthetic mappings created by :func:`aes`.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
    >>> ggplot(df, aes(x="x", y="y")) + geom_point()
    Plot(...)
    """
    return Plot(data=data, mapping=mapping or Aes())
