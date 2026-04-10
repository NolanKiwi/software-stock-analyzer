"""
Analysis functions for the software-sector stock dashboard.
"""

from __future__ import annotations

import pandas as pd
import numpy as np


# ---------------------------------------------------------------------------
# Ranking & sorting
# ---------------------------------------------------------------------------

def rank_by_decline(df: pd.DataFrame) -> pd.DataFrame:
    """Sort by 52-week decline (most declined first)."""
    return df.sort_values("decline_from_high_pct", ascending=True).reset_index(drop=True)


def rank_by_day_change(df: pd.DataFrame) -> pd.DataFrame:
    """Sort by today's change (biggest drop first)."""
    return df.sort_values("day_change_pct", ascending=True).reset_index(drop=True)


def get_top_decliners(df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    return rank_by_decline(df).head(n)


# ---------------------------------------------------------------------------
# Aggregations
# ---------------------------------------------------------------------------

def category_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("category")
        .agg(
            종목수=("ticker", "count"),
            평균하락률=("decline_from_high_pct", "mean"),
            최대하락=("decline_from_high_pct", "min"),
            당일평균등락=("day_change_pct", "mean"),
        )
        .round(2)
        .sort_values("평균하락률", ascending=True)
        .reset_index()
    )


def sub_industry_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("sub_industry")
        .agg(
            종목수=("ticker", "count"),
            평균하락률=("decline_from_high_pct", "mean"),
            당일평균등락=("day_change_pct", "mean"),
        )
        .round(2)
        .sort_values("평균하락률", ascending=True)
        .reset_index()
    )


def decline_distribution(df: pd.DataFrame) -> pd.DataFrame:
    bins   = [-100, -70, -50, -30, -20, -10, 0, 10]
    labels = ["70%+ 하락","50~70% 하락","30~50% 하락","20~30% 하락","10~20% 하락","0~10% 하락","상승"]
    df = df.copy()
    df["bucket"] = pd.cut(
        df["decline_from_high_pct"], bins=bins, labels=labels, right=True
    )
    counts = df.groupby("bucket", observed=True).size().reset_index(name="종목수")
    return counts


def summary_stats(df: pd.DataFrame) -> dict:
    if df.empty:
        return {}

    valid = df.dropna(subset=["decline_from_high_pct", "day_change_pct"])
    if valid.empty:
        return {}

    worst_row = valid.loc[valid["decline_from_high_pct"].idxmin()]
    best_row  = valid.loc[valid["decline_from_high_pct"].idxmax()]
    drop_row  = valid.loc[valid["day_change_pct"].idxmin()]
    gain_row  = valid.loc[valid["day_change_pct"].idxmax()]

    return {
        "total":               len(df),
        "avg_decline":         round(valid["decline_from_high_pct"].mean(), 2),
        "median_decline":      round(valid["decline_from_high_pct"].median(), 2),
        "worst_ticker":        worst_row["ticker"],
        "worst_name":          worst_row["name_en"],
        "worst_decline":       round(worst_row["decline_from_high_pct"], 2),
        "best_ticker":         best_row["ticker"],
        "best_name":           best_row["name_en"],
        "best_decline":        round(best_row["decline_from_high_pct"], 2),
        "day_drop_ticker":     drop_row["ticker"],
        "day_drop_name":       drop_row["name_en"],
        "day_drop_pct":        round(drop_row["day_change_pct"], 2),
        "day_gain_ticker":     gain_row["ticker"],
        "day_gain_name":       gain_row["name_en"],
        "day_gain_pct":        round(gain_row["day_change_pct"], 2),
        "pct_down_today":      round((valid["day_change_pct"] < 0).mean() * 100, 1),
        "pct_down_30_from_high": round((valid["decline_from_high_pct"] <= -30).mean() * 100, 1),
    }
