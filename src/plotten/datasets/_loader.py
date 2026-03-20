"""Dataset loading utilities.

All datasets are bundled with the package — no extra dependencies required.
"""

from __future__ import annotations

import narwhals as nw

from plotten._defaults import detect_backend
from plotten._validation import DataError

_SMALL_DATASETS = frozenset({"mtcars", "iris", "faithful", "tips", "mpg", "penguins"})
_ALL_DATASETS = sorted([*_SMALL_DATASETS, "diamonds"])


def _load_diamonds() -> dict[str, list]:
    """Load diamonds from the bundled gzipped CSV."""
    import csv
    import gzip
    from pathlib import Path

    csv_path = Path(__file__).parent / "diamonds.csv.gz"
    result: dict[str, list] = {}
    with gzip.open(csv_path, "rt", newline="") as f:
        reader = csv.DictReader(f)
        for col in reader.fieldnames or []:
            result[col] = []
        for row in reader:
            for col, val in row.items():
                result[col].append(val)

    # Cast numeric columns
    int_cols = {"price"}
    float_cols = {"carat", "depth", "table", "x", "y", "z"}
    for col in int_cols:
        if col in result:
            result[col] = [int(v) for v in result[col]]
    for col in float_cols:
        if col in result:
            result[col] = [float(v) for v in result[col]]

    return result


def load_dataset(name: str) -> nw.DataFrame:
    """Load a built-in example dataset.

    Parameters
    ----------
    name : str
        Dataset name (case-insensitive). One of: "diamonds", "faithful",
        "iris", "mpg", "mtcars", "penguins", "tips".

    Returns
    -------
    nw.DataFrame
        A narwhals DataFrame. Call ``.to_native()`` to unwrap to the
        underlying polars/pandas frame.

    Raises
    ------
    DataError
        If the dataset name is not recognized.

    Notes
    -----
    See ``plotten.datasets._data`` for full dataset citations and licenses.
    """
    key = name.lower().strip()

    if key in _SMALL_DATASETS:
        from plotten.datasets import _data

        data_dict = getattr(_data, f"_{key}")()
    elif key == "diamonds":
        data_dict = _load_diamonds()
    else:
        available = ", ".join(_ALL_DATASETS)
        msg = f"Unknown dataset {name!r}. Available datasets: {available}"
        raise DataError(msg)

    return nw.from_dict(data_dict, backend=detect_backend())
