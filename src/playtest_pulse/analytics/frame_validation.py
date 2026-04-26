from __future__ import annotations

import pandas as pd


# ---------------------------------------------------------------------------
# require_columns
#
# Verifies that a DataFrame contains the columns needed by a metric.
# ---------------------------------------------------------------------------
def require_columns(frame: pd.DataFrame, columns: list[str]) -> None:
    missing_columns = [column for column in columns if column not in frame.columns]

    if missing_columns:
        joined_columns = ", ".join(missing_columns)
        raise ValueError(f"events DataFrame is missing columns: {joined_columns}")
