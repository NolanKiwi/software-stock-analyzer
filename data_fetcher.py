"""
Fetches stock price data for the entire software sector universe via yfinance.
Supports caching (CSV / SQLite) with resumable collection and fallback snapshot.
"""

from __future__ import annotations

import logging
import sqlite3
import time
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import yfinance as yf

from stock_universe import build_universe

logger = logging.getLogger(__name__)

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
CSV_PATH       = DATA_DIR / "stocks.csv"
DB_PATH        = DATA_DIR / "stocks.db"
SNAPSHOT_PATH  = DATA_DIR / "snapshots.csv"
UNIVERSE_PATH  = DATA_DIR / "universe.csv"


# ---------------------------------------------------------------------------
# Single-ticker fetch
# ---------------------------------------------------------------------------

def _fetch_one(ticker: str, row: pd.Series) -> dict | None:
    """Fetch key stats for one ticker. Returns None on failure."""
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="1y")
        if hist.empty or len(hist) < 2:
            return None

        current  = float(hist["Close"].iloc[-1])
        high_52w = float(hist["High"].max())
        low_52w  = float(hist["Low"].min())
        prev     = float(hist["Close"].iloc[-2])
        day_chg  = current - prev
        day_pct  = (day_chg / prev * 100) if prev else 0.0
        decline  = ((current - high_52w) / high_52w * 100) if high_52w else 0.0

        info = {}
        try:
            info = t.info or {}
        except Exception:
            pass

        return {
            "ticker":                 ticker,
            "name_en":                row.get("name_en", info.get("longName", ticker)),
            "sub_industry":           row.get("sub_industry", "Other"),
            "category":               row.get("category", "기타"),
            "source":                 row.get("source", ""),
            "current_price":          round(current, 4),
            "prev_close":             round(prev, 4),
            "day_change":             round(day_chg, 4),
            "day_change_pct":         round(day_pct, 2),
            "high_52w":               round(high_52w, 4),
            "low_52w":                round(low_52w, 4),
            "decline_from_high_pct":  round(decline, 2),
            "market_cap":             info.get("marketCap"),
            "volume":                 info.get("volume"),
            "currency":               info.get("currency", "USD"),
            "updated_at":             datetime.now().isoformat(timespec="seconds"),
        }
    except Exception as exc:
        logger.warning("Failed %s: %s", ticker, exc)
        return None


# ---------------------------------------------------------------------------
# Batch fetch
# ---------------------------------------------------------------------------

def fetch_all(universe: pd.DataFrame | None = None, delay: float = 0.4) -> pd.DataFrame:
    """
    Fetch current stats for every ticker in *universe*.
    Returns a DataFrame sorted by decline_from_high_pct (most declined first).
    """
    if universe is None:
        universe = build_universe()

    rows = []
    total = len(universe)
    for i, (_, urow) in enumerate(universe.iterrows(), 1):
        ticker = urow["ticker"]
        logger.info("[%d/%d] %s", i, total, ticker)
        result = _fetch_one(ticker, urow)
        if result:
            rows.append(result)
        time.sleep(delay)

    df = pd.DataFrame(rows)
    if not df.empty:
        df.sort_values("decline_from_high_pct", ascending=True, inplace=True)
        df.reset_index(drop=True, inplace=True)
    return df


# ---------------------------------------------------------------------------
# Historical OHLCV
# ---------------------------------------------------------------------------

def fetch_history(ticker: str, period: str = "1y") -> pd.DataFrame:
    try:
        hist = yf.Ticker(ticker).history(period=period)
        hist.index = pd.to_datetime(hist.index).tz_localize(None)
        return hist
    except Exception as exc:
        logger.warning("History failed for %s: %s", ticker, exc)
        return pd.DataFrame()


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

def save_csv(df: pd.DataFrame) -> None:
    df.to_csv(CSV_PATH, index=False)

def load_csv() -> pd.DataFrame:
    return pd.read_csv(CSV_PATH) if CSV_PATH.exists() else pd.DataFrame()

def save_sqlite(df: pd.DataFrame) -> None:
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("stocks", conn, if_exists="replace", index=False)
    conn.close()

def load_sqlite() -> pd.DataFrame:
    if not DB_PATH.exists():
        return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM stocks", conn)
    conn.close()
    return df

def append_snapshot(df: pd.DataFrame) -> None:
    snap = df.copy()
    snap["snapshot_time"] = datetime.now().isoformat(timespec="seconds")
    mode = "a" if SNAPSHOT_PATH.exists() else "w"
    snap.to_csv(SNAPSHOT_PATH, mode=mode, header=(mode == "w"), index=False)

def is_stale(max_age_minutes: int = 30) -> bool:
    if not CSV_PATH.exists():
        return True
    age = datetime.now() - datetime.fromtimestamp(CSV_PATH.stat().st_mtime)
    return age > timedelta(minutes=max_age_minutes)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_data(force_refresh: bool = False) -> pd.DataFrame:
    """
    Load data for the full software-sector universe.
    Uses cached CSV if fresh; otherwise fetches live from yfinance.
    Falls back to built-in snapshot if live fetch fails.
    """
    if not force_refresh and not is_stale():
        df = load_csv()
        if not df.empty:
            logger.info("Loaded %d rows from cache", len(df))
            return df

    universe = build_universe()
    if not universe.empty:
        try:
            _save_universe(universe)
        except Exception:
            pass

    try:
        df = fetch_all(universe)
    except Exception as exc:
        logger.warning("fetch_all raised: %s — using snapshot fallback", exc)
        df = pd.DataFrame()

    if not df.empty:
        try:
            save_csv(df)
            save_sqlite(df)
            append_snapshot(df)
        except Exception as exc:
            logger.warning("Persist failed: %s", exc)
        return df

    logger.warning("Live fetch empty — falling back to snapshot")
    from snapshot_data import get_snapshot_df
    return get_snapshot_df()


def _save_universe(universe: pd.DataFrame) -> None:
    universe.to_csv(UNIVERSE_PATH, index=False)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    df = get_data(force_refresh=True)
    print(df[["ticker", "name_en", "category", "current_price",
              "day_change_pct", "decline_from_high_pct"]].to_string())
    print(f"\nTotal: {len(df)} companies fetched")
