"""Context manager for temporary plotten option overrides."""

from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator

    from plotten.themes._theme import Theme


@contextmanager
def options(
    *,
    theme: Theme | None = None,
    strict: bool | None = None,
    lazy_select: bool | None = None,
) -> Generator[None]:
    """Temporarily override global plotten options.

    Any options set inside the block are restored to their previous values
    when the block exits, even if an exception is raised.

    Parameters
    ----------
    theme : Theme, optional
        A theme to set as the global default for the duration of the block.
    strict : bool, optional
        Enable or disable strict mode (warnings become errors) for the
        duration of the block.
    lazy_select : bool, optional
        Enable column projection for lazy frames. When ``True``, lazy
        frames are narrowed to only the columns referenced by aesthetic
        mappings before ``.collect()`` is called. This enables projection
        pushdown — the backend can skip reading unused columns from disk.
        Has no effect on eager frames.

    Examples
    --------
    >>> from plotten import options, theme_dark, ggplot, aes, geom_point
    >>> import pandas as pd
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
    >>> p = ggplot(df, aes(x="x", y="y")) + geom_point()
    >>> with options(theme=theme_dark()):
    ...     p.show()  # doctest: +SKIP
    """
    from plotten._validation import (
        get_lazy_select,
        get_strict,
        set_lazy_select,
        set_strict,
    )
    from plotten.themes._theme import theme_set

    old_theme = None
    old_strict = None
    old_lazy_select = None
    try:
        if theme is not None:
            old_theme = theme_set(theme)
        if strict is not None:
            old_strict = get_strict()
            set_strict(strict)
        if lazy_select is not None:
            old_lazy_select = get_lazy_select()
            set_lazy_select(lazy_select)
        yield
    finally:
        if old_theme is not None:
            theme_set(old_theme)
        if old_strict is not None:
            set_strict(old_strict)
        if old_lazy_select is not None:
            set_lazy_select(old_lazy_select)
