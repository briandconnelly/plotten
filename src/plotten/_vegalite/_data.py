"""DataFrame → Vega-Lite data serialization."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

import narwhals as nw


def serialize_data(df: Any) -> list[dict[str, Any]]:
    """Convert a narwhals-compatible frame to a list of records for VL."""
    frame = nw.from_native(df)
    if hasattr(frame, "collect"):
        frame = frame.collect()
    # Convert to pandas for reliable dict serialization
    pdf = frame.to_pandas()
    records: list[dict[str, Any]] = pdf.to_dict(orient="records")
    # Ensure datetime columns are ISO 8601 strings
    for rec in records:
        for key, val in rec.items():
            if isinstance(val, (datetime, date)):
                rec[key] = val.isoformat()
    return records
