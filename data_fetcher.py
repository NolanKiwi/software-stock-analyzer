"""
Fetches stock price data for software/tech companies via yfinance.
Supports caching to CSV and SQLite with resumable collection.
"""

import sqlite3
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import yfinance as yf

from companies import COMPANIES, TICKERS

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
CSV_PATH = DATA_DIR / "stocks.csv"
DB_PATH = DATA_DIR / "stocks.db"
SNAPSHOT_PATH = DATA_DIR / "snapshot.csv"


# ---------------------------------------------------------------------------
# Low-level yfinance helpers
# ---------------------------------------------------------------------------

def _fetch_ticker_info(ticker: str) -> dict:
    """Return key stats for a single ticker."""
    try:
        t = yf.Ticker(ticker)
        info = t.info
        hist = t.history(period="1y")

        if hist.empty:
            return {}

        current_price = hist["Close"].iloc[-1]
        high_52w = hist["High"].max()
        low_52w = hist["Low"].min()
        prev_close = hist["Close"].iloc[-2] if len(hist) > 1 else current_price
        day_change = current_price - prev_close
        day_change_pct = (day_change / prev_close * 100) if prev_close else 0
        decline_from_high = ((current_price - high_52w) / high_52w * 100) if high_52w else 0

        meta = COMPANIES.get(ticker, {})

        return {
            "ticker": ticker,
            "name_kr": meta.get("name_kr", ticker),
            "name_en": meta.get("name_en", info.get("longName", ticker)),
            "sector": meta.get("sector", info.get("sector", "Unknown")),
            "exchange": meta.get("exchange", info.get("exchange", "Unknown")),
            "current_price": round(current_price, 4),
            "prev_close": round(prev_close, 4),
            "day_change": round(day_change, 4),
            "day_change_pct": round(day_change_pct, 2),
            "high_52w": round(high_52w, 4),
            "low_52w": round(low_52w, 4),
            "decline_from_high_pct": round(decline_from_high, 2),
            "market_cap": info.get("marketCap", None),
            "volume": info.get("volume", None),
            "currency": info.get("currency", "USD"),
            "updated_at": datetime.now().isoformat(),
        }
    except Exception as exc:
        logger.warning("Failed to fetch %s: %s", ticker, exc)
        return {}


def fetch_all(tickers: list[str] | None = None, delay: float = 0.5) -> pd.DataFrame:
    """
    Fetch current stats for all tickers.  Returns a DataFrame sorted by
    decline_from_high_pct (most declined first).
    """
    tickers = tickers or TICKERS
    rows = []
    for i, ticker in enumerate(tickers, 1):
        logger.info("[%d/%d] Fetching %s …", i, len(tickers), ticker)
        row = _fetch_ticker_info(ticker)
        if row:
            rows.append(row)
        time.sleep(delay)

    df = pd.DataFrame(rows)
    if not df.empty:
        df.dropna(subset=["current_price", "decline_from_high_pct"], inplace=True)
        df.sort_values("decline_from_high_pct", ascending=True, inplace=True)
        df.reset_index(drop=True, inplace=True)
    return df


# ---------------------------------------------------------------------------
# Historical OHLCV
# ---------------------------------------------------------------------------

def fetch_history(ticker: str, period: str = "1y") -> pd.DataFrame:
    """Return OHLCV history for one ticker."""
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period=period)
        hist.index = pd.to_datetime(hist.index)
        hist.index = hist.index.tz_localize(None)
        return hist
    except Exception as exc:
        logger.warning("History fetch failed for %s: %s", ticker, exc)
        return pd.DataFrame()


# ---------------------------------------------------------------------------
# Persistence helpers
# ---------------------------------------------------------------------------

def save_csv(df: pd.DataFrame, path: Path = CSV_PATH) -> None:
    df.to_csv(path, index=False)
    logger.info("Saved CSV → %s", path)


def load_csv(path: Path = CSV_PATH) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def save_sqlite(df: pd.DataFrame, path: Path = DB_PATH) -> None:
    conn = sqlite3.connect(path)
    df.to_sql("stocks", conn, if_exists="replace", index=False)
    conn.close()
    logger.info("Saved SQLite → %s", path)


def load_sqlite(path: Path = DB_PATH) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    conn = sqlite3.connect(path)
    df = pd.read_sql("SELECT * FROM stocks", conn)
    conn.close()
    return df


def save_snapshot(df: pd.DataFrame) -> None:
    """Append current snapshot with timestamp for historical tracking."""
    df = df.copy()
    df["snapshot_time"] = datetime.now().isoformat()
    if SNAPSHOT_PATH.exists():
        existing = pd.read_csv(SNAPSHOT_PATH)
        df = pd.concat([existing, df], ignore_index=True)
    df.to_csv(SNAPSHOT_PATH, index=False)


def is_data_stale(path: Path = CSV_PATH, max_age_minutes: int = 30) -> bool:
    if not path.exists():
        return True
    mtime = datetime.fromtimestamp(path.stat().st_mtime)
    return datetime.now() - mtime > timedelta(minutes=max_age_minutes)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_data(force_refresh: bool = False) -> pd.DataFrame:
    """
    Return a DataFrame of all companies.
    Uses cached CSV unless data is stale or force_refresh is True.
    Falls back to the hardcoded snapshot if live data is unavailable.
    """
    from snapshot_data import get_snapshot_df

    if not force_refresh and not is_data_stale():
        df = load_csv()
        if not df.empty:
            logger.info("Loaded from cache (%s)", CSV_PATH)
            return df

    try:
        df = fetch_all()
    except Exception as exc:
        logger.warning("fetch_all failed: %s — using snapshot fallback", exc)
        df = pd.DataFrame()

    if not df.empty:
        try:
            save_csv(df)
            save_sqlite(df)
            save_snapshot(df)
        except Exception as exc:
            logger.warning("Could not persist data: %s", exc)
        return df

    logger.warning("Live fetch returned no data — falling back to snapshot")
    return get_snapshot_df()


if __name__ == "__main__":
    print("Fetching data for all companies …")
    df = get_data(force_refresh=True)
    print(df[["ticker", "name_kr", "current_price", "day_change_pct", "decline_from_high_pct"]].to_string())
