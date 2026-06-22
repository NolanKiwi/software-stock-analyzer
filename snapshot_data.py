"""
Fallback snapshot data — used when live yfinance fetch fails.

Snapshot date: 2026-04-10  (sourced from reference image + estimated values)
"""

import pandas as pd

from stock_universe import SUBINDUSTRY_CATEGORY, TICKER_SUBINDUSTRY_OVERRIDES

SNAPSHOT_DATE = "2026-04-10"

# fmt: off
_ROWS = [
    # ticker, name_en, sub_industry, category, source,
    # current_price, day_change, day_change_pct,
    # high_52w, low_52w, decline_from_high_pct, currency
    # ── S&P 500 Application Software ─────────────────────────────────────────
    ("ADBE",  "Adobe Inc.",              "Application Software",                  "애플리케이션 소프트웨어", "S&P 500", 228.93,  -10.38,  -4.33,  570.00, 190.00, -59.84, "USD"),
    ("APP",   "AppLovin",                "Application Software",                  "애플리케이션 소프트웨어", "S&P 500", 310.50,  -18.20,  -5.54,  523.65, 35.00,  -40.71, "USD"),
    ("ADSK",  "Autodesk",                "Application Software",                  "애플리케이션 소프트웨어", "S&P 500", 265.40,   -9.10,  -3.31,  310.05, 195.00, -14.40, "USD"),
    ("CDNS",  "Cadence Design Systems",  "Application Software",                  "애플리케이션 소프트웨어", "S&P 500", 235.80,   -8.90,  -3.64,  310.40, 200.00, -24.03, "USD"),
    ("DDOG",  "Datadog",                 "Application Software",                  "애플리케이션 소프트웨어", "S&P 500", 100.50,   -5.30,  -5.01,  175.65,  88.00, -42.77, "USD"),
    ("FICO",  "Fair Isaac",              "Application Software",                  "애플리케이션 소프트웨어", "S&P 500",1800.00,  -75.00,  -4.00, 2590.00,1200.00, -30.50, "USD"),
    ("INTU",  "Intuit",                  "Application Software",                  "애플리케이션 소프트웨어", "S&P 500", 369.88,  -18.44,  -4.74,  723.40, 348.00, -48.87, "USD"),
    ("ORCL",  "Oracle Corporation",      "Application Software",                  "애플리케이션 소프트웨어", "S&P 500", 158.20,   -6.10,  -3.72,  198.00, 100.00, -20.10, "USD"),
    ("PLTR",  "Palantir Technologies",   "Application Software",                  "애플리케이션 소프트웨어", "S&P 500", 130.97,   -9.79,  -6.95,  185.00,  16.50, -29.20, "USD"),
    ("PTC",   "PTC Inc.",                "Application Software",                  "애플리케이션 소프트웨어", "S&P 500", 170.50,   -7.50,  -4.21,  210.00, 155.00, -18.81, "USD"),
    ("CRM",   "Salesforce",              "Application Software",                  "애플리케이션 소프트웨어", "S&P 500", 168.11,   -7.82,  -4.44,  369.00, 153.00, -54.44, "USD"),
    ("NOW",   "ServiceNow",              "Application Software",                  "애플리케이션 소프트웨어", "S&P 500",  92.17,   -5.30,  -5.43,  237.00,  75.00, -61.11, "USD"),
    ("SNPS",  "Synopsys",                "Application Software",                  "애플리케이션 소프트웨어", "S&P 500", 430.20,  -16.80,  -3.76,  610.00, 380.00, -29.47, "USD"),
    ("TYL",   "Tyler Technologies",      "Application Software",                  "애플리케이션 소프트웨어", "S&P 500", 570.00,  -22.00,  -3.72,  710.00, 480.00, -19.72, "USD"),
    ("WDAY",  "Workday, Inc.",           "Application Software",                  "애플리케이션 소프트웨어", "S&P 500", 195.30,   -9.10,  -4.45,  310.00, 180.00, -36.99, "USD"),
    # ── S&P 500 Systems Software / Security ──────────────────────────────────
    ("CRWD",  "CrowdStrike Holdings",    "Systems Software",                      "시스템 소프트웨어 / 보안", "S&P 500", 409.00,  -17.51,  -4.10,  570.35, 210.00, -28.29, "USD"),
    ("FTNT",  "Fortinet",               "Systems Software",                      "시스템 소프트웨어 / 보안", "S&P 500",  98.50,   -3.80,  -3.72,  112.50,  57.00, -12.44, "USD"),
    ("GEN",   "Gen Digital",            "Systems Software",                      "시스템 소프트웨어 / 보안", "S&P 500",  22.80,   -0.80,  -3.39,   28.50,  17.00, -20.00, "USD"),
    ("MSFT",  "Microsoft",              "Systems Software",                      "시스템 소프트웨어 / 보안", "S&P 500", 385.50,  -15.20,  -3.79,  468.35, 344.00, -17.70, "USD"),
    ("PANW",  "Palo Alto Networks",     "Systems Software",                      "시스템 소프트웨어 / 보안", "S&P 500", 168.34,   -5.40,  -3.13,  227.25, 155.00, -25.89, "USD"),
    # ── S&P 500 Internet Services & Infrastructure ────────────────────────────
    ("AKAM",  "Akamai Technologies",    "Internet Services & Infrastructure",    "인터넷 / 클라우드 인프라", "S&P 500",  82.50,   -3.20,  -3.74,  120.00,  70.00, -31.25, "USD"),
    ("GDDY",  "GoDaddy",               "Internet Services & Infrastructure",    "인터넷 / 클라우드 인프라", "S&P 500", 155.80,   -5.90,  -3.65,  200.00, 120.00, -22.10, "USD"),
    ("VRSN",  "Verisign",              "Internet Services & Infrastructure",    "인터넷 / 클라우드 인프라", "S&P 500", 190.50,   -6.50,  -3.30,  230.00, 170.00, -17.17, "USD"),
    # ── S&P 500 IT Consulting ─────────────────────────────────────────────────
    ("ACN",   "Accenture",             "IT Consulting & Other Services",        "IT 컨설팅 / 서비스",      "S&P 500", 285.40,  -11.20,  -3.78,  380.00, 255.00, -24.89, "USD"),
    ("CTSH",  "Cognizant",             "IT Consulting & Other Services",        "IT 컨설팅 / 서비스",      "S&P 500",  65.80,   -2.50,  -3.66,   78.00,  55.00, -15.64, "USD"),
    ("EPAM",  "EPAM Systems",          "IT Consulting & Other Services",        "IT 컨설팅 / 서비스",      "S&P 500", 185.00,   -7.00,  -3.64,  280.00, 148.00, -33.93, "USD"),
    ("IT",    "Gartner",               "IT Consulting & Other Services",        "IT 컨설팅 / 서비스",      "S&P 500", 450.00,  -17.00,  -3.64,  600.00, 390.00, -25.00, "USD"),
    ("IBM",   "IBM",                   "IT Consulting & Other Services",        "IT 컨설팅 / 서비스",      "S&P 500", 215.00,   -7.80,  -3.50,  240.00, 155.00, -10.42, "USD"),
    # ── Supplementary: Cybersecurity ─────────────────────────────────────────
    ("ZS",    "Zscaler",               "Systems Software",                      "시스템 소프트웨어 / 보안", "Supplementary", 165.50,  -8.20,  -4.72,  265.00, 130.00, -37.55, "USD"),
    ("OKTA",  "Okta",                  "Systems Software",                      "시스템 소프트웨어 / 보안", "Supplementary",  88.20,  -4.50,  -4.85,  180.00,  65.00, -51.00, "USD"),
    ("S",     "SentinelOne",           "Systems Software",                      "시스템 소프트웨어 / 보안", "Supplementary",  16.50,  -0.90,  -5.17,   34.50,  12.00, -52.17, "USD"),
    ("CYBR",  "CyberArk Software",     "Systems Software",                      "시스템 소프트웨어 / 보안", "Supplementary", 285.00, -13.50,  -4.52,  420.00, 220.00, -32.14, "USD"),
    ("NET",   "Cloudflare",            "Internet Services & Infrastructure",    "인터넷 / 클라우드 인프라", "Supplementary",  90.50,  -4.80,  -5.04,  135.00,  55.00, -32.96, "USD"),
    ("TENB",  "Tenable Holdings",      "Systems Software",                      "시스템 소프트웨어 / 보안", "Supplementary",  40.50,  -1.60,  -3.80,   62.00,  30.00, -34.68, "USD"),
    ("QLYS",  "Qualys",                "Systems Software",                      "시스템 소프트웨어 / 보안", "Supplementary", 125.00,  -4.40,  -3.40,  175.00, 115.00, -28.57, "USD"),
    ("RPD",   "Rapid7",                "Systems Software",                      "시스템 소프트웨어 / 보안", "Supplementary",  28.50,  -1.40,  -4.68,   62.00,  24.00, -54.03, "USD"),
    ("CHKP",  "Check Point Software",  "Systems Software",                      "시스템 소프트웨어 / 보안", "Supplementary", 190.00,  -6.50,  -3.30,  230.00, 155.00, -17.39, "USD"),
    ("VRNS",  "Varonis Systems",       "Systems Software",                      "시스템 소프트웨어 / 보안", "Supplementary",  42.80,  -2.20,  -4.89,   65.00,  30.00, -34.15, "USD"),
    ("BB",    "BlackBerry",            "Systems Software",                      "시스템 소프트웨어 / 보안", "Supplementary",   3.80,  -0.12,  -3.06,    6.00,   2.20, -36.67, "USD"),
    ("FSLY",  "Fastly",                "Internet Services & Infrastructure",    "인터넷 / 클라우드 인프라", "Supplementary",   7.20,  -0.42,  -5.51,   25.00,   5.50, -71.20, "USD"),
    # ── Supplementary: Cloud / SaaS ──────────────────────────────────────────
    ("SNOW",  "Snowflake",             "Application Software",                  "애플리케이션 소프트웨어", "Supplementary", 120.50,  -6.80,  -5.34,  240.00,  90.00, -49.79, "USD"),
    ("HUBS",  "HubSpot",              "Application Software",                  "애플리케이션 소프트웨어", "Supplementary", 380.00, -18.00,  -4.52,  680.00, 320.00, -44.12, "USD"),
    ("VEEV",  "Veeva Systems",        "Application Software",                  "애플리케이션 소프트웨어", "Supplementary", 192.00,  -7.50,  -3.76,  250.00, 150.00, -23.20, "USD"),
    ("MDB",   "MongoDB",              "Application Software",                  "애플리케이션 소프트웨어", "Supplementary", 185.00,  -9.50,  -4.89,  450.00, 130.00, -58.89, "USD"),
    ("ZM",    "Zoom Video",           "Application Software",                  "애플리케이션 소프트웨어", "Supplementary",  70.50,  -3.20,  -4.34,   88.00,  55.00, -19.89, "USD"),
    ("TWLO",  "Twilio",               "Application Software",                  "애플리케이션 소프트웨어", "Supplementary",  52.80,  -2.80,  -5.03,   95.00,  40.00, -44.42, "USD"),
    ("CFLT",  "Confluent",            "Application Software",                  "애플리케이션 소프트웨어", "Supplementary",  22.50,  -1.20,  -5.06,   40.00,  15.00, -43.75, "USD"),
    ("ESTC",  "Elastic N.V.",         "Application Software",                  "애플리케이션 소프트웨어", "Supplementary",  75.00,  -3.80,  -4.83,  120.00,  55.00, -37.50, "USD"),
    ("DOCN",  "DigitalOcean",         "Internet Services & Infrastructure",    "인터넷 / 클라우드 인프라", "Supplementary",  30.50,  -1.50,  -4.69,   52.00,  22.00, -41.35, "USD"),
    ("DOMO",  "Domo",                 "Application Software",                  "애플리케이션 소프트웨어", "Supplementary",   7.40,  -0.35,  -4.52,   14.00,   6.00, -47.14, "USD"),
    ("BAND",  "Bandwidth",            "Application Software",                  "애플리케이션 소프트웨어", "Supplementary",  15.20,  -0.80,  -5.00,   28.00,  11.00, -45.71, "USD"),
    # ── Supplementary: Dev Tools ─────────────────────────────────────────────
    ("TEAM",  "Atlassian",            "Application Software",                  "애플리케이션 소프트웨어", "Supplementary", 185.00,  -9.00,  -4.64,  280.00, 140.00, -33.93, "USD"),
    ("GTLB",  "GitLab",              "Application Software",                  "애플리케이션 소프트웨어", "Supplementary",  42.50,  -2.20,  -4.92,   72.00,  30.00, -40.97, "USD"),
    ("APPN",  "Appian",              "Application Software",                  "애플리케이션 소프트웨어", "Supplementary",  25.80,  -1.20,  -4.44,   48.00,  18.00, -46.25, "USD"),
    ("FROG",  "JFrog",               "Application Software",                  "애플리케이션 소프트웨어", "Supplementary",  22.50,  -1.10,  -4.67,   40.00,  16.00, -43.75, "USD"),
    ("U",     "Unity Software",      "Application Software",                  "애플리케이션 소프트웨어", "Supplementary",  18.50,  -1.00,  -5.13,   48.00,  12.00, -61.46, "USD"),
    ("RBLX",  "Roblox",              "Application Software",                  "애플리케이션 소프트웨어", "Supplementary",  32.50,  -1.80,  -5.25,   55.00,  22.00, -40.91, "USD"),
    # ── Supplementary: Fintech Software ──────────────────────────────────────
    ("PAYC",  "Paycom Software",     "Application Software",                  "애플리케이션 소프트웨어", "Supplementary", 145.00,  -6.50,  -4.29,  265.00, 115.00, -45.28, "USD"),
    ("PCTY",  "Paylocity",           "Application Software",                  "애플리케이션 소프트웨어", "Supplementary", 125.00,  -5.80,  -4.43,  210.00,  98.00, -40.48, "USD"),
    ("BILL",  "Bill.com Holdings",   "Application Software",                  "애플리케이션 소프트웨어", "Supplementary",  42.80,  -2.10,  -4.68,  160.00,  35.00, -73.25, "USD"),
    ("QTWO",  "Q2 Holdings",          "Application Software",                  "애플리케이션 소프트웨어", "Supplementary",  82.00,  -3.10,  -3.64,  112.00,  52.00, -26.79, "USD"),
    ("HOOD",  "Robinhood Markets",   "Application Software",                  "애플리케이션 소프트웨어", "Supplementary",  69.42,  -2.41,  -3.35,  149.76,  17.36, -53.65, "USD"),
    ("COIN",  "Coinbase Global",     "Application Software",                  "애플리케이션 소프트웨어", "Supplementary", 169.69,  -5.40,  -3.08,  349.75, 123.50, -51.48, "USD"),
    ("CRCL",  "Circle Internet Group","Application Software",                 "애플리케이션 소프트웨어", "Supplementary",  89.77,  -4.67,  -4.94,  299.00,  55.00, -70.01, "USD"),
    # ── Supplementary: AI Software ───────────────────────────────────────────
    ("AI",    "C3.ai",               "Application Software",                  "애플리케이션 소프트웨어", "Supplementary",  18.50,  -1.10,  -5.61,   40.00,  15.00, -53.75, "USD"),
    ("PATH",  "UiPath",              "Application Software",                  "애플리케이션 소프트웨어", "Supplementary",  11.80,  -0.70,  -5.60,   28.00,   8.50, -57.86, "USD"),
    ("BBAI",  "BigBear.ai",          "Application Software",                  "애플리케이션 소프트웨어", "Supplementary",   1.95,  -0.12,  -5.80,   9.80,   1.20, -80.10, "USD"),
    ("SOUN",  "SoundHound AI",       "Application Software",                  "애플리케이션 소프트웨어", "Supplementary",   5.80,  -0.38,  -6.15,  24.98,   2.50, -76.78, "USD"),
    ("TEM",   "Tempus AI",           "Application Software",                  "애플리케이션 소프트웨어", "Supplementary",  45.84,  -1.66,  -3.49,  104.34,  21.00, -56.05, "USD"),
    # ── Supplementary: Other ─────────────────────────────────────────────────
    ("FIG",   "Figma",               "Application Software",                  "애플리케이션 소프트웨어", "Supplementary",  19.42,  -0.73,  -3.62,   55.00,  12.00, -64.69, "USD"),
    ("MNTS",  "Momentus",            "Application Software",                  "애플리케이션 소프트웨어", "Supplementary",   3.50,  -0.14,  -3.84,   45.60,   2.30, -92.32, "USD"),
    ("RSLS",  "Resolve Medical",     "Application Software",                  "애플리케이션 소프트웨어", "Supplementary",   2.63,  -0.19,  -6.73,   12.50,   1.80, -78.96, "USD"),
    # ── ETFs ─────────────────────────────────────────────────────────────────
    ("IGV",   "iShares Expanded Tech-Software ETF",  "ETF", "ETF", "Supplementary",  76.84, -2.91,  -3.64, 120.00,  62.00, -35.97, "USD"),
    ("WCLD",  "WisdomTree Cloud Computing ETF",      "ETF", "ETF", "Supplementary",  20.50, -0.95,  -4.43,  32.00,  16.00, -35.94, "USD"),
    ("BUG",   "Global X Cybersecurity ETF",          "ETF", "ETF", "Supplementary",  18.20, -0.72,  -3.80,  25.00,  14.00, -27.20, "USD"),
    ("SKYY",  "First Trust Cloud Computing ETF",     "ETF", "ETF", "Supplementary",  75.50, -3.10,  -3.94, 110.00,  60.00, -31.36, "USD"),
    ("CIBR",  "First Trust Nasdaq Cybersecurity ETF", "ETF", "ETF", "Supplementary",  65.20, -2.10,  -3.12,  76.00,  55.00, -14.21, "USD"),
    ("CLOU",  "Global X Cloud Computing ETF",        "ETF", "ETF", "Supplementary",  14.80, -0.65,  -4.21,  22.00,  11.00, -32.73, "USD"),
    ("CONL",  "GraniteShares 2x Long COIN ETF",      "ETF", "ETF", "Supplementary",   6.58, -0.43,  -6.13,  57.00,   3.00, -88.46, "USD"),
]
# fmt: on

_COLS = [
    "ticker", "name_en", "sub_industry", "category", "source",
    "current_price", "day_change", "day_change_pct",
    "high_52w", "low_52w", "decline_from_high_pct", "currency",
]


def get_snapshot_df() -> pd.DataFrame:
    df = pd.DataFrame(_ROWS, columns=_COLS)
    df["sub_industry"] = df.apply(
        lambda row: TICKER_SUBINDUSTRY_OVERRIDES.get(row["ticker"], row["sub_industry"]),
        axis=1,
    )
    df["category"] = df["sub_industry"].map(SUBINDUSTRY_CATEGORY).fillna("기타")
    df["prev_close"]  = df["current_price"] - df["day_change"]
    df["market_cap"]  = None
    df["volume"]      = None
    df["updated_at"]  = f"{SNAPSHOT_DATE}T00:00:00 (스냅샷)"
    df.sort_values("decline_from_high_pct", ascending=True, inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df
