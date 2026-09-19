"""
engagement.py
Build the Engagement Index — a single composite score combining
JobInvolvement, JobSatisfaction, EnvironmentSatisfaction, and
RelationshipSatisfaction (each on a 1-4 scale).

Pulled out of notebook 02 so the dashboard can compute the same index
live (e.g. when a user changes a filter) without duplicating the formula.
"""

import pandas as pd

ENGAGEMENT_COLS = [
    "JobInvolvement",
    "JobSatisfaction",
    "EnvironmentSatisfaction",
    "RelationshipSatisfaction",
]


def add_engagement_index(df: pd.DataFrame, cols=None) -> pd.DataFrame:
    """
    Add two columns to the DataFrame:
    - EngagementRaw: simple mean of the 4 satisfaction columns (still 1-4 scale)
    - EngagementIndex: EngagementRaw rescaled (normalized) to a 0-1 range,
      so it reads like a percentage-style score
    Returns a new DataFrame; does not modify the input in place.
    """
    cols = cols or ENGAGEMENT_COLS
    df = df.copy()

    df["EngagementRaw"] = df[cols].mean(axis=1)

    min_raw, max_raw = df["EngagementRaw"].min(), df["EngagementRaw"].max()
    if max_raw == min_raw:
        # Avoid divide-by-zero if every row happens to score identically
        df["EngagementIndex"] = 0.5
    else:
        df["EngagementIndex"] = (df["EngagementRaw"] - min_raw) / (max_raw - min_raw)

    return df


def engagement_tier(score: float) -> str:
    """Bucket a single 0-1 EngagementIndex value into Low / Medium / High."""
    if score < 0.34:
        return "Low"
    elif score < 0.67:
        return "Medium"
    else:
        return "High"


def add_engagement_tier(df: pd.DataFrame) -> pd.DataFrame:
    """Add an EngagementTier column (Low/Medium/High) from EngagementIndex."""
    df = df.copy()
    df["EngagementTier"] = df["EngagementIndex"].apply(engagement_tier)
    return df


def score(df: pd.DataFrame) -> pd.DataFrame:
    """Convenience function: add both EngagementIndex and EngagementTier."""
    df = add_engagement_index(df)
    df = add_engagement_tier(df)
    return df
