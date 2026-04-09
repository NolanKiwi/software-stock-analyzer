"""
Price-decline analysis for software/tech stocks.
"""

from __future__ import annotations

import pandas as pd
import numpy as np


def rank_by_decline(df: pd.DataFrame) -> pd.DataFrame:
    """Sort by largest decline from 52-week high (ascending = most declined first)."""
    return df.sort_values("decline_from_high_pct", ascending=True).reset_index(drop=True)


def sector_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate average decline and count per sector."""
    return (
        df.groupby("sector")
        .agg(
            count=("ticker", "count"),
            avg_decline=("decline_from_high_pct", "mean"),
            avg_day_change=("day_change_pct", "mean"),
        )
        .round(2)
        .sort_values("avg_decline", ascending=True)
        .reset_index()
    )


def get_top_decliners(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    return rank_by_decline(df).head(n)


def summary_stats(df: pd.DataFrame) -> dict:
    """Return a dict of headline numbers for the dashboard."""
    if df.empty:
        return {}

    worst = df.loc[df["decline_from_high_pct"].idxmin()]
    best = df.loc[df["decline_from_high_pct"].idxmax()]
    biggest_day_drop = df.loc[df["day_change_pct"].idxmin()]

    return {
        "total_companies": len(df),
        "avg_decline_from_high": round(df["decline_from_high_pct"].mean(), 2),
        "median_decline_from_high": round(df["decline_from_high_pct"].median(), 2),
        "worst_ticker": worst["ticker"],
        "worst_name_kr": worst["name_kr"],
        "worst_decline": round(worst["decline_from_high_pct"], 2),
        "best_ticker": best["ticker"],
        "best_name_kr": best["name_kr"],
        "best_decline": round(best["decline_from_high_pct"], 2),
        "biggest_day_drop_ticker": biggest_day_drop["ticker"],
        "biggest_day_drop_pct": round(biggest_day_drop["day_change_pct"], 2),
        "pct_down_today": round(
            (df["day_change_pct"] < 0).sum() / len(df) * 100, 1
        ),
    }


def decline_buckets(df: pd.DataFrame) -> pd.DataFrame:
    """Bucket stocks by severity of decline from 52-week high."""
    bins = [-100, -50, -30, -20, -10, 0]
    labels = ["50%+ 하락", "30~50% 하락", "20~30% 하락", "10~20% 하락", "0~10% 하락"]
    df = df.copy()
    df["bucket"] = pd.cut(
        df["decline_from_high_pct"], bins=bins, labels=labels, right=True
    )
    return df.groupby("bucket", observed=True).size().reset_index(name="count")
