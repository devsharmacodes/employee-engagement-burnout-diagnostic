"""
burnout.py
Compute the Burnout Risk Score from OverTime, WorkLifeBalance, and
(optionally) EngagementIndex.

Pulled out of notebook 03. Requires EngagementIndex to already exist on
the DataFrame — run engagement.score() first.
"""

import pandas as pd


def add_burnout_flag(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add the core binary burnout flag used in the project brief:
    OverTime = Yes AND WorkLifeBalance <= 2.
    Also adds the two underlying component flags for transparency.
    """
    df = df.copy()
    df["OverTimeFlag"] = (df["OverTime"] == "Yes").astype(int)
    df["LowWLBFlag"] = (df["WorkLifeBalance"] <= 2).astype(int)
    df["BurnoutFlag"] = ((df["OverTimeFlag"] == 1) & (df["LowWLBFlag"] == 1)).astype(int)
    return df


def _risk_level(row: pd.Series) -> str:
    """
    Score 0-4 points from overtime, work-life balance, and low engagement,
    then map to a Low / Medium / High risk label. See burnout_risk() for
    how points are assigned.
    """
    pts = 0
    if row["OverTime"] == "Yes":
        pts += 1
    if row["WorkLifeBalance"] <= 2:
        pts += 2
    elif row["WorkLifeBalance"] == 3:
        pts += 1
    if row.get("EngagementIndex", 1) < 0.34:
        pts += 1

    if pts >= 3:
        return "High"
    elif pts >= 1:
        return "Medium"
    else:
        return "Low"


def add_burnout_risk(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a BurnoutRisk column (Low/Medium/High), combining overtime,
    work-life balance, and engagement into one risk level. This is
    broader than the binary BurnoutFlag — it also catches employees
    who are trending toward burnout but don't hit both flags yet.
    """
    df = df.copy()
    df["BurnoutRisk"] = df.apply(_risk_level, axis=1)
    return df


def score(df: pd.DataFrame) -> pd.DataFrame:
    """Convenience function: add both BurnoutFlag and BurnoutRisk."""
    df = add_burnout_flag(df)
    df = add_burnout_risk(df)
    return df
