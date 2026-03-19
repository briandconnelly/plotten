"""Font registration and Google Fonts integration."""

from __future__ import annotations

import os
import re
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

from matplotlib.font_manager import FontProperties, fontManager

from plotten._validation import PlottenError

_FONT_EXTENSIONS = {".ttf", ".otf"}
_CACHE_DIR = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "plotten" / "fonts"

# User-Agent that causes Google Fonts CSS API to return TTF URLs
# (without it, the API returns woff2 which matplotlib can't read).
_UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"

# All CSS2 axis-range weights so we get every weight variant in one request.
_ALL_WEIGHTS = "200;300;400;500;600;700;800;900"


def register_font(path: str | Path) -> str:
    """Register a TTF/OTF font file with matplotlib and return its family name.

    Parameters
    ----------
    path : str or Path
        Path to a ``.ttf`` or ``.otf`` font file.

    Returns
    -------
    str
        The font family name, for use in ``theme(font_family=name)``
        or ``element_text(family=name)``.

    Raises
    ------
    PlottenError
        If the file does not exist or has an unsupported extension.
    """
    p = Path(path)
    if not p.exists():
        msg = f"Font file not found: {p}"
        raise PlottenError(msg)
    if p.suffix.lower() not in _FONT_EXTENSIONS:
        msg = f"Unsupported font extension '{p.suffix}'. Use .ttf or .otf."
        raise PlottenError(msg)

    fontManager.addfont(str(p))
    name = FontProperties(fname=str(p)).get_name()
    return name


def available_fonts() -> list[str]:
    """Return sorted list of all available font family names."""
    return sorted({f.name for f in fontManager.ttflist})


def register_google_font(family: str, *, weight: str = "regular") -> str:
    """Download and register a Google Font.

    Uses the Google Fonts CSS2 API to discover TTF file URLs, downloads
    them to ``$XDG_CACHE_HOME/plotten/fonts/<family>/`` (defaulting to
    ``~/.cache/…``), and registers every file with matplotlib.

    Parameters
    ----------
    family : str
        The Google Font family name (e.g. ``"Roboto"``).
    weight : str
        Unused currently — all available weights are downloaded.

    Returns
    -------
    str
        The font family name as registered with matplotlib.

    Raises
    ------
    PlottenError
        If the download fails or no font files are found.
    """
    cache_dir = _CACHE_DIR / family
    font_files = _cached_font_files(cache_dir)

    if not font_files:
        font_files = _download_google_font(family, cache_dir)

    name = ""
    for f in font_files:
        name = register_font(f)
    return name


def _download_google_font(family: str, cache_dir: Path) -> list[Path]:
    """Fetch font files for *family* via the Google Fonts CSS2 API."""
    quoted = quote(family)
    css_url = f"https://fonts.googleapis.com/css2?family={quoted}:wght@{_ALL_WEIGHTS}"

    try:
        req = Request(css_url, headers={"User-Agent": _UA})
        css = urlopen(req).read().decode()
    except Exception as exc:
        msg = f"Failed to fetch Google Font '{family}': {exc}"
        raise PlottenError(msg) from exc

    # Extract TTF/OTF URLs from the CSS @font-face blocks
    urls = re.findall(r"url\((https://[^)]+\.(?:ttf|otf))\)", css)
    if not urls:
        msg = (
            f"No font files found for '{family}'. "
            "Check that the family name is spelled exactly as on fonts.google.com."
        )
        raise PlottenError(msg)

    cache_dir.mkdir(parents=True, exist_ok=True)

    downloaded: list[Path] = []
    for i, url in enumerate(urls):
        ext = ".ttf" if url.endswith(".ttf") else ".otf"
        dest = cache_dir / f"{family}-{i}{ext}"
        try:
            data = urlopen(url).read()
        except Exception as exc:
            msg = f"Failed to download font file from {url}: {exc}"
            raise PlottenError(msg) from exc
        dest.write_bytes(data)
        downloaded.append(dest)

    return downloaded


def _cached_font_files(cache_dir: Path) -> list[Path]:
    """Return font files already present in *cache_dir*."""
    if not cache_dir.exists():
        return []
    return sorted(p for p in cache_dir.rglob("*") if p.suffix.lower() in _FONT_EXTENSIONS)
