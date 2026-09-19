"""
metrics.py
Organization-level KPI (Key Performance Indicator) calculations, as listed
in the project brief:
- Engagement Index (see engagement.py for the per-employee version)
- Burnout Risk Score (see burnout.py for the per-employee version)
- Work-Life Balance Index
- Satisfaction Stability Score
- Workload Stress Indicator

Each function here takes a (already-scored) DataFrame and returns a
single summary number or small summary table — meant for dashboard
headline metrics, not per-employee detail.
"""

import pandas as pd

SATISFACTION_COLS = [
    "JobInvolvement",
    "JobSatisfaction",
    "EnvironmentSatisfaction",
    "RelationshipSatisfaction",
]


def org_engagement_index(df: pd.DataFrame) -> float:
    """Average EngagementIndex across the given group of employees (0-1)."""
    return round(df["EngagementIndex"].mean(), 3)


def work_life_balance_index(df: pd.DataFrame) -> float:
    """Average WorkLifeBalance rating (1-4 scale) across the group."""
    return round(df["WorkLifeBalance"].mean(), 2)


def burnout_risk_breakdown(df: pd.DataFrame) -> pd.Series:
    """
    Share of employees (%) at each BurnoutRisk level (Low/Medium/High)
    within the given group.
    """
    return (df["BurnoutRisk"].value_counts(normalize=True) * 100).round(1)


def satisfaction_stability_score(df: pd.DataFrame) -> float:
    """
    How consistent an employee's satisfaction is across the four
    satisfaction dimensions, averaged across the group. Computed as
    1 minus the average row-wise standard deviation (rescaled to 0-1),
    so a higher score = more stable/consistent satisfaction, a lower
    score = satisfaction swings a lot between dimensions (e.g. loves
    the job environment but hates their relationships at work).
    """
    row_std = df[SATISFACTION_COLS].std(axis=1)
    # Max possible std on a 1-4 scale with 4 values is bounded; normalize
    # against the observed max in this dataset so the score stays 0-1.
    max_std = row_std.max() if row_std.max() > 0 else 1
    stability = 1 - (row_std / max_std)
    return round(stability.mean(), 3)


def workload_stress_indicator(df: pd.DataFrame) -> float:
    """
    Share (%) of employees who both travel frequently and work overtime —
    the combination the project brief calls out as the workload/stress
    intensity signal.
    """
    stressed = df[(df["OverTime"] == "Yes") & (df["BusinessTravel"] == "Travel_Frequently")]
    if len(df) == 0:
        return 0.0
    return round(len(stressed) / len(df) * 100, 1)


def kpi_summary(df: pd.DataFrame) -> dict:
    """
    Bundle every headline KPI into one dict — handy for rendering the
    dashboard's top summary row in a single call.
    """
    return {
        "Engagement Index": org_engagement_index(df),
        "Work-Life Balance Index": work_life_balance_index(df),
        "Satisfaction Stability Score": satisfaction_stability_score(df),
        "Workload Stress Indicator (%)": workload_stress_indicator(df),
        "High Burnout Risk (%)": burnout_risk_breakdown(df).get("High", 0.0),
    }
