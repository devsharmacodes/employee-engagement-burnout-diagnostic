"""
data_loader.py
Load and clean the Palo Alto Networks HR dataset.

This module pulls the logic out of notebook 01 so both future notebooks
and the Streamlit dashboard can reuse the exact same cleaning steps
instead of duplicating code.
"""

import os
import pandas as pd

ORDINAL_COLS = [
    "EnvironmentSatisfaction",
    "JobInvolvement",
    "JobSatisfaction",
    "RelationshipSatisfaction",
    "WorkLifeBalance",
]


def load_raw(path: str = "data/raw/Palo_Alto_Networks.csv") -> pd.DataFrame:
    """Load the untouched raw CSV exactly as provided."""
    return pd.read_csv(path)


def validate_ordinal_ranges(df: pd.DataFrame, cols=None) -> pd.DataFrame:
    """
    Return a small report (one row per column) showing the min/max value
    found and how many rows fall outside the expected 1-4 range.
    Use this to sanity-check the data before trusting it.
    """
    cols = cols or ORDINAL_COLS
    rows = []
    for c in cols:
        out_of_range = df[~df[c].between(1, 4)]
        rows.append({
            "column": c,
            "min": df[c].min(),
            "max": df[c].max(),
            "out_of_range_rows": len(out_of_range),
        })
    return pd.DataFrame(rows)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply the standard cleaning steps:
    - drop exact duplicate rows
    - normalize Attrition to 0/1 integers
    - strip whitespace from key categorical columns
    Returns a new, cleaned DataFrame (does not modify the input in place).
    """
    df = df.copy()
    df = df.drop_duplicates()

    if df["Attrition"].dtype == object:
        df["Attrition"] = df["Attrition"].map({"Yes": 1, "No": 0, 1: 1, 0: 0})

    df["OverTime"] = df["OverTime"].astype(str).str.strip()
    df["Department"] = df["Department"].astype(str).str.strip()

    return df


def load_clean(raw_path: str = "data/raw/Palo_Alto_Networks.csv") -> pd.DataFrame:
    """Convenience function: load the raw CSV and clean it in one call."""
    return clean(load_raw(raw_path))


def save(df: pd.DataFrame, path: str) -> None:
    """Save a DataFrame to CSV, creating the destination folder if needed."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
