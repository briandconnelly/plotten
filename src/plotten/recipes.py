"""Plot recipes — high-level constructors for common plot patterns.

Each recipe composes existing plotten geoms into a complete Plot,
saving users from repetitive boilerplate.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from typing import Literal

import narwhals as nw

from plotten._aes import aes
from plotten._labs import labs
from plotten._plot import Plot, ggplot
from plotten.geoms import (
    geom_errorbarh,
    geom_line,
    geom_point,
    geom_rect,
    geom_segment,
    geom_text,
    geom_tile,
    geom_vline,
)
from plotten.themes import theme_minimal


def _get_backend(data: Any) -> Literal["pandas", "polars"]:
    """Detect the native narwhals backend name."""
    native = nw.get_native_namespace(nw.from_native(data))
    return "polars" if "polars" in str(native) else "pandas"


def plot_waterfall(
    data: Any,
    *,
    x: str,
    y: str,
    fill_increase: str = "#2ecc71",
    fill_decrease: str = "#e74c3c",
    fill_total: str = "#3498db",
    total_label: str | None = "Total",
    connector: bool = True,
    connector_color: str = "#888888",
    width: float = 0.7,
    title: str | None = None,
) -> Plot:
    """Create a waterfall chart showing cumulative effect of sequential values.

    Parameters
    ----------
    data : DataFrame
        Input data (any narwhals-compatible frame).
    x : str
        Column for category labels (x-axis).
    y : str
        Column for values (positive = increase, negative = decrease).
    fill_increase, fill_decrease, fill_total : str
        Colors for increasing, decreasing, and total bars.
    total_label : str or None
        Label for the total bar. None to omit.
    connector : bool
        Draw connector lines between bars.
    width : float
        Bar width (0-1).
    title : str or None
        Plot title.
    """
    frame = nw.from_native(data)
    x_vals = frame.get_column(x).to_list()
    y_vals = frame.get_column(y).to_list()
    backend = _get_backend(data)

    bar_labels = list(x_vals)
    ymins: list[float] = []
    ymaxs: list[float] = []
    categories: list[str] = []
    cumulative = 0.0

    for v in y_vals:
        v = float(v)
        ymins.append(cumulative)
        cumulative += v
        ymaxs.append(cumulative)
        categories.append("increase" if v >= 0 else "decrease")

    if total_label is not None:
        bar_labels.append(total_label)
        ymins.append(0.0)
        ymaxs.append(cumulative)
        categories.append("total")

    n = len(bar_labels)
    x_pos = list(range(n))
    half_w = width / 2

    color_map = {"increase": fill_increase, "decrease": fill_decrease, "total": fill_total}
    fill_colors = [color_map[c] for c in categories]

    rect_data = nw.to_native(
        nw.from_dict(
            {
                "xmin": [p - half_w for p in x_pos],
                "xmax": [p + half_w for p in x_pos],
                "ymin": ymins,
                "ymax": ymaxs,
                "fill": fill_colors,
            },
            backend=backend,
        )
    )

    p = (
        ggplot(rect_data, aes(xmin="xmin", xmax="xmax", ymin="ymin", ymax="ymax"))
        + geom_rect(fill=True)
        + theme_minimal()
    )

    if connector and n > 1:
        seg_x: list[float] = []
        seg_xend: list[float] = []
        seg_y: list[float] = []
        seg_yend: list[float] = []
        for i in range(n - 1):
            seg_x.append(x_pos[i] + half_w)
            seg_xend.append(x_pos[i + 1] - half_w)
            seg_y.append(ymaxs[i])
            seg_yend.append(ymaxs[i])

        conn_data = nw.to_native(
            nw.from_dict(
                {"x": seg_x, "xend": seg_xend, "y": seg_y, "yend": seg_yend},
                backend=backend,
            )
        )
        p = p + geom_segment(
            data=conn_data,
            mapping=aes(x="x", xend="xend", y="y", yend="yend"),
            color=connector_color,
            linetype="--",
            size=0.5,
        )

    if title is not None:
        p = p + labs(title=title)

    return p


def plot_dumbbell(
    data: Any,
    *,
    x_start: str,
    x_end: str,
    y: str,
    color_start: str = "#e74c3c",
    color_end: str = "#2ecc71",
    segment_color: str = "#cccccc",
    segment_size: float = 1.5,
    point_size: float = 50,
    title: str | None = None,
) -> Plot:
    """Create a dumbbell chart comparing two values per category.

    Parameters
    ----------
    data : DataFrame
        Input data.
    x_start, x_end : str
        Columns for the start and end values.
    y : str
        Column for category labels.
    color_start, color_end : str
        Point colors for start and end values.
    segment_color : str
        Color of the connecting segment.
    segment_size : float
        Width of the connecting segment.
    point_size : float
        Size of the endpoint markers.
    title : str or None
        Plot title.
    """
    frame = nw.from_native(data)
    backend = _get_backend(data)
    y_labels = frame.get_column(y).to_list()
    n = len(y_labels)
    y_positions = list(range(n))

    # Build numeric data for segments and points
    num_data = nw.to_native(
        nw.from_dict(
            {
                "x_start": frame.get_column(x_start).to_list(),
                "x_end": frame.get_column(x_end).to_list(),
                "y_pos": y_positions,
                "y_end": y_positions,
            },
            backend=backend,
        )
    )

    from plotten.scales import scale_y_continuous

    p = (
        ggplot(num_data)
        + geom_segment(
            x="x_start",
            xend="x_end",
            y="y_pos",
            yend="y_end",
            color=segment_color,
            size=segment_size,
        )
        + geom_point(x="x_start", y="y_pos", color=color_start, size=point_size)
        + geom_point(x="x_end", y="y_pos", color=color_end, size=point_size)
        + scale_y_continuous(breaks=y_positions, labels=[str(v) for v in y_labels])
        + theme_minimal()
    )

    if title is not None:
        p = p + labs(title=title)

    return p


def plot_lollipop(
    data: Any,
    *,
    x: str,
    y: str,
    color: str = "#3498db",
    point_size: float = 50,
    stem_size: float = 1.5,
    horizontal: bool = False,
    baseline: float = 0.0,
    title: str | None = None,
) -> Plot:
    """Create a lollipop chart (stems with dots).

    Parameters
    ----------
    data : DataFrame
        Input data.
    x, y : str
        Column names for positions and values.
    color : str
        Color for stems and dots.
    point_size : float
        Size of the dot markers.
    stem_size : float
        Width of the stems.
    horizontal : bool
        If True, stems are horizontal.
    baseline : float
        Value where stems start (default 0).
    title : str or None
        Plot title.
    """
    frame = nw.from_native(data)
    backend = _get_backend(data)

    x_vals = frame.get_column(x).to_list()
    y_vals = frame.get_column(y).to_list()

    if horizontal:
        seg_data = nw.to_native(
            nw.from_dict(
                {
                    "x": [baseline] * len(x_vals),
                    "xend": y_vals,
                    "y": x_vals,
                    "yend": x_vals,
                },
                backend=backend,
            )
        )
        pt_data = nw.to_native(nw.from_dict({"x": y_vals, "y": x_vals}, backend=backend))
    else:
        seg_data = nw.to_native(
            nw.from_dict(
                {
                    "x": x_vals,
                    "xend": x_vals,
                    "y": [baseline] * len(y_vals),
                    "yend": y_vals,
                },
                backend=backend,
            )
        )
        pt_data = nw.to_native(nw.from_dict({"x": x_vals, "y": y_vals}, backend=backend))

    p = (
        ggplot()
        + geom_segment(
            data=seg_data,
            x="x",
            xend="xend",
            y="y",
            yend="yend",
            color=color,
            size=stem_size,
        )
        + geom_point(data=pt_data, x="x", y="y", color=color, size=point_size)
        + theme_minimal()
    )

    if title is not None:
        p = p + labs(title=title)

    return p


def plot_slope(
    data: Any,
    *,
    x: str,
    y: str,
    group: str,
    color: str | None = None,
    label: bool = True,
    label_size: float = 8,
    title: str | None = None,
) -> Plot:
    """Create a slope chart comparing values across two time points.

    Parameters
    ----------
    data : DataFrame
        Input data with exactly two unique values in the x column.
    x : str
        Column with time-point identifiers (should have exactly 2 unique values).
    y : str
        Column with numeric values.
    group : str
        Column identifying each line/entity.
    color : str or None
        Fixed color for all lines, or None for default.
    label : bool
        Whether to label endpoints with group names.
    label_size : float
        Font size for endpoint labels.
    title : str or None
        Plot title.
    """
    line_params: dict[str, Any] = {"group": group}
    if color is not None:
        line_params["color"] = color

    p = (
        ggplot(data, aes(x=x, y=y))
        + geom_line(**line_params)
        + geom_point(**line_params)
        + theme_minimal()
    )

    if label:
        frame = nw.from_native(data)
        x_vals = frame.get_column(x).unique().sort().to_list()
        if len(x_vals) >= 2:
            # Label at the last x value — rename group col to 'label' to avoid
            # conflict with the group aesthetic
            last_x = x_vals[-1]
            label_frame = frame.filter(nw.col(x) == last_x)
            label_frame = label_frame.with_columns(nw.col(group).cast(nw.String).alias("_label"))
            label_data = nw.to_native(label_frame)
            p = p + geom_text(
                data=label_data,
                x=x,
                y=y,
                label="_label",
                ha="left",
                size=label_size,
            )

    if title is not None:
        p = p + labs(title=title)

    return p


def plot_forest(
    data: Any,
    *,
    y: str,
    x: str,
    xmin: str,
    xmax: str,
    vline: float = 0.0,
    vline_linetype: str = "--",
    vline_color: str = "#999999",
    point_size: float = 50,
    color: str = "#333333",
    title: str | None = None,
) -> Plot:
    """Create a forest plot for meta-analysis or effect-size comparison.

    Parameters
    ----------
    data : DataFrame
        Input data.
    y : str
        Column for study/category labels.
    x : str
        Column for point estimates (effect sizes).
    xmin, xmax : str
        Columns for confidence interval bounds.
    vline : float
        Position of the null-effect reference line.
    vline_linetype : str
        Line style for the reference line.
    vline_color : str
        Color of the reference line.
    point_size : float
        Size of the point estimate markers.
    color : str
        Color for points and error bars.
    title : str or None
        Plot title.
    """
    p = (
        ggplot(data, aes(x=x, y=y))
        + geom_vline(xintercept=vline, linetype=vline_linetype, color=vline_color)
        + geom_errorbarh(xmin=xmin, xmax=xmax, y=y, color=color, height=0.2)
        + geom_point(color=color, size=point_size)
        + theme_minimal()
    )

    if title is not None:
        p = p + labs(title=title)

    return p


def plot_waffle(
    data: Any,
    *,
    category: str,
    value: str,
    rows: int = 10,
    cols: int = 10,
    colors: dict[str, str] | list[str] | None = None,
    title: str | None = None,
    show_legend: bool = True,
) -> Plot:
    """Create a waffle chart — a grid of squares showing proportions.

    Parameters
    ----------
    data : DataFrame
        Input data (any narwhals-compatible frame).
    category : str
        Column with category labels.
    value : str
        Column with numeric counts or proportions.
    rows : int
        Number of rows in the waffle grid (default 10).
    cols : int
        Number of columns in the waffle grid (default 10).
    colors : dict or list or None
        Category-to-color mapping (dict), ordered color list, or None for defaults.
    title : str or None
        Plot title.
    show_legend : bool
        Whether to show a fill legend (default True).
    """
    from plotten.coords import coord_equal
    from plotten.scales import scale_fill_manual, scale_x_continuous, scale_y_continuous
    from plotten.themes import element_blank, theme

    frame = nw.from_native(data)
    backend = _get_backend(data)

    cat_vals = frame.get_column(category).to_list()
    num_vals = [float(v) for v in frame.get_column(value).to_list()]

    total_cells = rows * cols
    total_value = sum(num_vals)

    # Allocate cells proportionally, ensuring they sum to total_cells
    raw_shares = [v / total_value * total_cells for v in num_vals]
    cell_counts = [int(s) for s in raw_shares]
    remainder = total_cells - sum(cell_counts)
    # Distribute remaining cells by largest fractional remainder
    fractions = [s - int(s) for s in raw_shares]
    for _ in range(remainder):
        idx = max(range(len(fractions)), key=lambda i: fractions[i])
        cell_counts[idx] += 1
        fractions[idx] = -1  # don't pick again

    # Build grid: fill left-to-right, bottom-to-top
    grid_cats: list[str] = []
    for cat, count in zip(cat_vals, cell_counts, strict=True):
        grid_cats.extend([cat] * count)

    x_positions: list[int] = []
    y_positions: list[int] = []
    fill_vals: list[str] = []

    for i, cat in enumerate(grid_cats):
        col_idx = i // rows
        row_idx = i % rows
        x_positions.append(col_idx)
        y_positions.append(row_idx)
        fill_vals.append(cat)

    # Resolve colors
    if colors is None:
        color_map = None
    elif isinstance(colors, dict):
        color_map = colors
    else:
        color_map = dict(zip(cat_vals, colors, strict=True))

    tile_data = nw.to_native(
        nw.from_dict(
            {"x": x_positions, "y": y_positions, "fill": fill_vals},
            backend=backend,
        )
    )

    p = (
        ggplot(tile_data, aes(x="x", y="y", fill="fill"))
        + geom_tile(color="white", width=0.9, height=0.9)
        + coord_equal()
    )

    if color_map is not None:
        p = p + scale_fill_manual(color_map)

    p = p + scale_x_continuous(expand=(0, 0.5)) + scale_y_continuous(expand=(0, 0.5))

    # Remove axes for a clean grid look
    p = (
        p
        + theme_minimal()
        + theme(
            axis_title_x=element_blank(),
            axis_title_y=element_blank(),
            axis_text_x=element_blank(),
            axis_text_y=element_blank(),
            axis_ticks=element_blank(),
            panel_grid_major=element_blank(),
            panel_grid_minor=element_blank(),
        )
    )

    if not show_legend:
        p = p + theme(legend_position="none")

    if title is not None:
        p = p + labs(title=title)

    return p
