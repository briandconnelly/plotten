"""DataFrame → Vega-Lite data serialization."""

from __future__ import annotations

import math
from datetime import date, datetime
from typing import Any

import narwhals as nw


def serialize_data(df: Any) -> list[dict[str, Any]]:
    """Convert a narwhals-compatible frame to a list of records for VL."""
    frame = nw.from_native(df)
    if hasattr(frame, "collect"):
        frame = frame.collect()
    records: list[dict[str, Any]] = [dict(row) for row in frame.iter_rows(named=True)]
    # Sanitize values for JSON compatibility
    for rec in records:
        for key, val in rec.items():
            if isinstance(val, (datetime, date)):
                rec[key] = val.isoformat()
            elif isinstance(val, float) and math.isnan(val):
                rec[key] = None
    return records
