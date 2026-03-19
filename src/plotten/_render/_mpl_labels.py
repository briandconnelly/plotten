"""Axis labels, title, subtitle, and caption application."""

from __future__ import annotations

from typing import TYPE_CHECKING

from plotten._defaults import (
    CAPTION_BOTTOM_PAD,
    CAPTION_X,
    CAPTION_Y,
    SUBTITLE_Y_NORMAL,
    SUBTITLE_Y_POLAR,
    TITLE_Y,
    TOP_BOTH_NORMAL,
    TOP_BOTH_POLAR,
    TOP_SINGLE_NORMAL,
    TOP_SINGLE_POLAR,
)

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

    from plotten._render._resolve import ResolvedPlot
    from plotten.themes._theme import Theme


def apply_axis_labs(ax: Axes, resolved: ResolvedPlot, theme: Theme) -> None:
    """Apply axis labels from labs. Call before tight_layout."""
    from plotten.coords._polar import CoordPolar

    labs = resolved.labs
    if labs is None:
        return
    # Polar axes don't use x/y axis labels — they overlap with angle/radius ticks
    if isinstance(resolved.coord, CoordPolar):
        return

    axis_title_x_size = getattr(theme, "axis_title_x_size", None) or theme.label_size
    axis_title_y_size = getattr(theme, "axis_title_y_size", None) or theme.label_size

    if labs.x is not None:
        ax.set_xlabel(labs.x, fontsize=axis_title_x_size)
    if labs.y is not None:
        ax.set_ylabel(labs.y, fontsize=axis_title_y_size)


def apply_title(fig: Figure, resolved: ResolvedPlot, theme: Theme) -> None:
    """Apply title, subtitle, and caption. Call after tight_layout."""
    from plotten.coords._polar import CoordPolar
    from plotten.themes._elements import ElementBlank, ElementText

    labs = resolved.labs
    if labs is None:
        return

    polar = isinstance(resolved.coord, CoordPolar)
    title_color = getattr(theme, "title_color", "#000000")
    title_size = theme.title_size
    title_family = theme.font_family
    subtitle_size = getattr(theme, "subtitle_size", None) or theme.label_size
    subtitle_color = getattr(theme, "subtitle_color", "#555555")

    # Apply element overrides
    if isinstance(theme.plot_title, ElementText):
        if theme.plot_title.size is not None:
            title_size = theme.plot_title.size
        if theme.plot_title.color is not None:
            title_color = theme.plot_title.color
        if theme.plot_title.family is not None:
            title_family = theme.plot_title.family

    if isinstance(theme.plot_subtitle, ElementText):
        if theme.plot_subtitle.size is not None:
            subtitle_size = theme.plot_subtitle.size
        if theme.plot_subtitle.color is not None:
            subtitle_color = theme.plot_subtitle.color

    has_title = labs.title is not None and not isinstance(theme.plot_title, ElementBlank)
    has_subtitle = labs.subtitle is not None and not isinstance(theme.plot_subtitle, ElementBlank)

    # Polar axes need more top margin since tick labels extend above the circle
    top_both = TOP_BOTH_POLAR if polar else TOP_BOTH_NORMAL
    top_single = TOP_SINGLE_POLAR if polar else TOP_SINGLE_NORMAL

    if has_title and has_subtitle:
        assert labs.title is not None
        assert labs.subtitle is not None
        sub_y = SUBTITLE_Y_POLAR if polar else SUBTITLE_Y_NORMAL
        fig.suptitle(
            labs.title,
            fontsize=title_size,
            fontfamily=title_family,
            color=title_color,
            y=TITLE_Y,
        )
        fig.text(
            0.5,
            sub_y,
            labs.subtitle,
            ha="center",
            va="top",
            fontsize=subtitle_size,
            fontfamily=theme.font_family,
            color=subtitle_color,
            transform=fig.transFigure,
        )
        fig.subplots_adjust(top=top_both)
    elif has_title:
        assert labs.title is not None
        fig.suptitle(
            labs.title,
            fontsize=title_size,
            fontfamily=title_family,
            color=title_color,
        )
        fig.subplots_adjust(top=top_single)
    elif has_subtitle:
        assert labs.subtitle is not None
        fig.suptitle(
            labs.subtitle,
            fontsize=subtitle_size,
            fontfamily=theme.font_family,
            color=subtitle_color,
        )
        fig.subplots_adjust(top=top_single)

    if labs.caption is not None and not isinstance(theme.plot_caption, ElementBlank):
        cur_bottom = fig.subplotpars.bottom
        fig.subplots_adjust(bottom=cur_bottom + CAPTION_BOTTOM_PAD)
        fig.text(
            CAPTION_X,
            CAPTION_Y,
            labs.caption,
            ha="right",
            va="bottom",
            fontsize=theme.tick_size,
            fontfamily=theme.font_family,
        )
