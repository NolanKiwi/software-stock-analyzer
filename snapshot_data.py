"""
Hardcoded snapshot from the reference image (2026-04-10) used as fallback
when live yfinance data is unavailable (e.g. cloud network restrictions).
"""

import pandas as pd
from datetime import datetime

SNAPSHOT_DATE = "2026-04-10"

_ROWS = [
    # ticker, name_kr, name_en, sector, exchange, current_price, day_change, day_change_pct, high_52w, low_52w, decline_from_high_pct, currency
    ("COIN",   "코인베이스 글로벌",              "Coinbase Global",                      "Fintech",              "NASDAQ", 169.69,  -5.40,   -3.08, 349.75,  123.50, -51.48, "USD"),
    ("PANW",   "팔로 알토 네트웍스",             "Palo Alto Networks",                   "Cybersecurity",        "NASDAQ", 168.34,  -5.40,   -3.13, 227.25,  155.00, -25.89, "USD"),
    ("TEM",    "템퍼스 AI",                    "Tempus AI",                            "AI / Healthcare",      "NASDAQ",  45.84,  -1.66,   -3.49, 104.34,  21.00,  -56.05, "USD"),
    ("HOOD",   "로빈후드",                     "Robinhood Markets",                    "Fintech",              "NASDAQ",  69.42,  -2.41,   -3.35, 149.76,  17.36,  -53.65, "USD"),
    ("SILC",   "실스크",                       "Silk (SILC)",                          "Software",             "NASDAQ",   2.06,  -0.08,   -3.73,   5.60,   1.50,  -63.21, "USD"),
    ("FIG",    "피그마",                       "Figma",                               "Design Software",      "NYSE",    19.42,  -0.73,   -3.62,  55.00,  12.00,  -64.69, "USD"),
    ("IGV",    "iShares 북미 소프트웨어 ETF",   "iShares Expanded Tech-Software ETF",  "ETF",                  "NYSE",    76.84,  -2.91,   -3.64, 120.00,  62.00,  -35.97, "USD"),
    ("MNTS",   "모멘터스",                     "Momentus",                            "Space Tech",           "NASDAQ",   3.50,  -0.14,   -3.84,  45.60,   2.30,  -92.32, "USD"),
    ("CRWD",   "크라우드스트라이크 홀딩스",      "CrowdStrike Holdings",                "Cybersecurity",        "NASDAQ", 409.00, -17.51,   -4.10, 570.35, 210.00,  -28.29, "USD"),
    ("ADBE",   "어도비",                       "Adobe",                               "Software",             "NASDAQ", 228.93, -10.38,   -4.33, 570.00, 190.00,  -59.84, "USD"),
    ("CRM",    "세일즈포스",                   "Salesforce",                          "CRM Software",         "NYSE",   168.11,  -7.82,   -4.44, 369.00, 153.00,  -54.44, "USD"),
    ("INTU",   "인튜이트",                     "Intuit",                              "Fintech Software",     "NASDAQ", 369.88, -18.44,   -4.74, 723.40, 348.00,  -48.87, "USD"),
    ("CRCL",   "써클 인터넷 그룹",              "Circle Internet Group",               "Fintech",              "NYSE",    89.77,  -4.67,   -4.94, 299.00,  55.00,  -70.01, "USD"),
    ("6324.T", "하모닉 드라이브 시스템스",       "Harmonic Drive Systems",              "Industrial / Robotics","TSE",   3940.00,-215.00,  -5.17,9900.00,2900.00, -60.20, "JPY"),
    ("NOW",    "서비스나우",                   "ServiceNow",                          "Enterprise Software",  "NYSE",    92.17,  -5.30,   -5.43, 237.00,  75.00,  -61.11, "USD"),
    ("CONL",   "GraniteShares 코인베이스 2X ETF","GraniteShares 2x Long COIN Daily ETF","ETF",                "NYSE",     6.58,  -0.43,   -6.13,  57.00,   3.00,  -88.46, "USD"),
    ("RSLS",   "리졸브 AI",                   "Resolve Medical",                     "AI",                   "NASDAQ",   2.63,  -0.19,   -6.73,  12.50,   1.80,  -78.96, "USD"),
    ("PLTR",   "팔란티어 테크놀로지스",          "Palantir Technologies",               "AI / Data Analytics",  "NASDAQ", 130.97,  -9.79,   -6.95, 185.00,  16.50,  -29.20, "USD"),
]

_COLUMNS = [
    "ticker", "name_kr", "name_en", "sector", "exchange",
    "current_price", "day_change", "day_change_pct",
    "high_52w", "low_52w", "decline_from_high_pct", "currency",
]


def get_snapshot_df() -> pd.DataFrame:
    df = pd.DataFrame(_ROWS, columns=_COLUMNS)
    df["prev_close"] = df["current_price"] - df["day_change"]
    df["market_cap"] = None
    df["volume"] = None
    df["updated_at"] = f"{SNAPSHOT_DATE}T00:00:00 (스냅샷)"
    df.sort_values("decline_from_high_pct", ascending=True, inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df
