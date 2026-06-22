"""
Builds the full software-sector stock universe.

Sources:
  1. S&P 500 via Wikipedia — Application Software, Systems Software,
     Internet Services & Infrastructure, IT Consulting & Other Services,
     Data Processing & Outsourced Services sub-industries.
  2. Curated supplementary list — important software companies outside
     the S&P 500, plus relevant ETFs.
"""

from __future__ import annotations

import logging
from io import StringIO

import pandas as pd
import requests

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Sub-industry → internal category mapping
# ---------------------------------------------------------------------------
SUBINDUSTRY_CATEGORY = {
    "Application Software":                      "SaaS / 애플리케이션",
    "Systems Software":                          "시스템 소프트웨어",
    "Internet Services & Infrastructure":        "인터넷 / 클라우드 인프라",
    "IT Consulting & Other Services":            "IT 컨설팅 / 서비스",
    "Data Processing & Outsourced Services":     "데이터 처리 / 아웃소싱",
    "Cybersecurity":                             "사이버보안",
    "Zero Trust / SASE":                         "사이버보안",
    "Identity Security":                         "사이버보안",
    "Vulnerability / Exposure Management":       "사이버보안",
    "CDN / Edge Network":                        "CDN / 엣지 인프라",
    "Cloud Infrastructure":                      "클라우드 인프라",
    "Observability / DevOps":                    "관측성 / DevOps",
    "Data Cloud / Analytics":                    "데이터 클라우드 / 분석",
    "ETF":                                       "ETF",
    "Other":                                     "기타",
}

# Human-readable Korean sub-industry name → used in UI
SUBINDUSTRY_KR = {v: v for v in SUBINDUSTRY_CATEGORY.values()}

# ---------------------------------------------------------------------------
# Supplementary tickers (not captured from S&P 500 table above)
# ---------------------------------------------------------------------------
SUPPLEMENTARY: dict[str, dict] = {
    # ── Cybersecurity ──────────────────────────────────────────────
    "ZS":    {"name_en": "Zscaler",                  "sub_industry": "Zero Trust / SASE"},
    "OKTA":  {"name_en": "Okta",                     "sub_industry": "Identity Security"},
    "S":     {"name_en": "SentinelOne",              "sub_industry": "Cybersecurity"},
    "CYBR":  {"name_en": "CyberArk Software",        "sub_industry": "Identity Security"},
    "TENB":  {"name_en": "Tenable Holdings",         "sub_industry": "Vulnerability / Exposure Management"},
    "QLYS":  {"name_en": "Qualys",                   "sub_industry": "Vulnerability / Exposure Management"},
    "RPD":   {"name_en": "Rapid7",                   "sub_industry": "Vulnerability / Exposure Management"},
    "VRNS":  {"name_en": "Varonis Systems",          "sub_industry": "Cybersecurity"},
    "CHKP":  {"name_en": "Check Point Software",     "sub_industry": "Cybersecurity"},
    "BB":    {"name_en": "BlackBerry",               "sub_industry": "Cybersecurity"},
    "SAIL":  {"name_en": "SailPoint",                "sub_industry": "Identity Security"},
    "RDWR":  {"name_en": "Radware",                  "sub_industry": "CDN / Edge Network"},
    "YOU":   {"name_en": "Clear Secure",             "sub_industry": "Identity Security"},
    # ── CDN / Edge ─────────────────────────────────────────────────
    "NET":   {"name_en": "Cloudflare",               "sub_industry": "CDN / Edge Network"},
    "FSLY":  {"name_en": "Fastly",                   "sub_industry": "CDN / Edge Network"},
    # ── Cloud / SaaS ───────────────────────────────────────────────
    "AMZN":  {"name_en": "Amazon.com",               "sub_industry": "Cloud Infrastructure"},
    "GOOGL": {"name_en": "Alphabet",                 "sub_industry": "Cloud Infrastructure"},
    "SNOW":  {"name_en": "Snowflake",                "sub_industry": "Data Cloud / Analytics"},
    "HUBS":  {"name_en": "HubSpot",                  "sub_industry": "Application Software"},
    "VEEV":  {"name_en": "Veeva Systems",            "sub_industry": "Application Software"},
    "MDB":   {"name_en": "MongoDB",                  "sub_industry": "Data Cloud / Analytics"},
    "ZM":    {"name_en": "Zoom Video Communications","sub_industry": "Application Software"},
    "TWLO":  {"name_en": "Twilio",                   "sub_industry": "Application Software"},
    "CFLT":  {"name_en": "Confluent",                "sub_industry": "Data Cloud / Analytics"},
    "ESTC":  {"name_en": "Elastic N.V.",             "sub_industry": "Observability / DevOps"},
    "DOCN":  {"name_en": "DigitalOcean",             "sub_industry": "Cloud Infrastructure"},
    "DOMO":  {"name_en": "Domo",                     "sub_industry": "Data Cloud / Analytics"},
    "BAND":  {"name_en": "Bandwidth",                "sub_industry": "Application Software"},
    # ── Dev Tools & Platforms ──────────────────────────────────────
    "TEAM":  {"name_en": "Atlassian",                "sub_industry": "Observability / DevOps"},
    "GTLB":  {"name_en": "GitLab",                   "sub_industry": "Observability / DevOps"},
    "APPN":  {"name_en": "Appian",                   "sub_industry": "Application Software"},
    "FROG":  {"name_en": "JFrog",                    "sub_industry": "Observability / DevOps"},
    "U":     {"name_en": "Unity Software",           "sub_industry": "Application Software"},
    "RBLX":  {"name_en": "Roblox",                   "sub_industry": "Application Software"},
    # ── Fintech Software ───────────────────────────────────────────
    "PAYC":  {"name_en": "Paycom Software",          "sub_industry": "Application Software"},
    "PCTY":  {"name_en": "Paylocity",                "sub_industry": "Application Software"},
    "BILL":  {"name_en": "Bill.com Holdings",        "sub_industry": "Application Software"},
    "QTWO":  {"name_en": "Q2 Holdings",              "sub_industry": "Application Software"},
    "HOOD":  {"name_en": "Robinhood Markets",        "sub_industry": "Application Software"},
    "COIN":  {"name_en": "Coinbase Global",          "sub_industry": "Application Software"},
    "CRCL":  {"name_en": "Circle Internet Group",   "sub_industry": "Application Software"},
    # ── AI / Data Software ─────────────────────────────────────────
    "AI":    {"name_en": "C3.ai",                    "sub_industry": "Application Software"},
    "PATH":  {"name_en": "UiPath",                   "sub_industry": "Data Cloud / Analytics"},
    "BBAI":  {"name_en": "BigBear.ai",               "sub_industry": "Application Software"},
    "SOUN":  {"name_en": "SoundHound AI",            "sub_industry": "Application Software"},
    "TEM":   {"name_en": "Tempus AI",                "sub_industry": "Application Software"},
    # ── Other Notable Software ─────────────────────────────────────
    "FIG":   {"name_en": "Figma",                    "sub_industry": "Application Software"},
    "MNTS":  {"name_en": "Momentus",                 "sub_industry": "Application Software"},
    "RSLS":  {"name_en": "Resolve Medical",          "sub_industry": "Application Software"},
    "SILC":  {"name_en": "Silk (SILC)",              "sub_industry": "Application Software"},
    "6324.T":{"name_en": "Harmonic Drive Systems",   "sub_industry": "Application Software"},
    # ── Software ETFs ──────────────────────────────────────────────
    "IGV":   {"name_en": "iShares Expanded Tech-Software ETF", "sub_industry": "ETF"},
    "WCLD":  {"name_en": "WisdomTree Cloud Computing ETF",      "sub_industry": "ETF"},
    "BUG":   {"name_en": "Global X Cybersecurity ETF",          "sub_industry": "ETF"},
    "SKYY":  {"name_en": "First Trust Cloud Computing ETF",     "sub_industry": "ETF"},
    "HACK":  {"name_en": "ETFMG Prime Cyber Security ETF",      "sub_industry": "ETF"},
    "CLOU":  {"name_en": "Global X Cloud Computing ETF",        "sub_industry": "ETF"},
    "CIBR":  {"name_en": "First Trust Nasdaq Cybersecurity ETF", "sub_industry": "ETF"},
    "CONL":  {"name_en": "GraniteShares 2x Long COIN ETF",      "sub_industry": "ETF"},
}

# S&P rows take precedence during de-duplication, so apply thematic overrides
# after merging. This keeps CDN/security/cloud leaders visible in the app.
TICKER_SUBINDUSTRY_OVERRIDES = {
    "AKAM": "CDN / Edge Network",
    "NET": "CDN / Edge Network",
    "FSLY": "CDN / Edge Network",
    "RDWR": "CDN / Edge Network",
    "CRWD": "Cybersecurity",
    "FTNT": "Cybersecurity",
    "PANW": "Cybersecurity",
    "GEN": "Cybersecurity",
    "ZS": "Zero Trust / SASE",
    "OKTA": "Identity Security",
    "CYBR": "Identity Security",
    "SAIL": "Identity Security",
    "YOU": "Identity Security",
    "S": "Cybersecurity",
    "CHKP": "Cybersecurity",
    "VRNS": "Cybersecurity",
    "BB": "Cybersecurity",
    "TENB": "Vulnerability / Exposure Management",
    "QLYS": "Vulnerability / Exposure Management",
    "RPD": "Vulnerability / Exposure Management",
    "AMZN": "Cloud Infrastructure",
    "GOOGL": "Cloud Infrastructure",
    "MSFT": "Cloud Infrastructure",
    "ORCL": "Cloud Infrastructure",
    "IBM": "Cloud Infrastructure",
    "DOCN": "Cloud Infrastructure",
    "DDOG": "Observability / DevOps",
    "TEAM": "Observability / DevOps",
    "GTLB": "Observability / DevOps",
    "FROG": "Observability / DevOps",
    "ESTC": "Observability / DevOps",
    "SNOW": "Data Cloud / Analytics",
    "MDB": "Data Cloud / Analytics",
    "CFLT": "Data Cloud / Analytics",
    "DOMO": "Data Cloud / Analytics",
    "PLTR": "Data Cloud / Analytics",
    "PATH": "Data Cloud / Analytics",
}

# S&P 500 sub-industries that belong to the software sector
_SP500_SOFTWARE_SUBINDUSTRIES = {
    "Application Software",
    "Systems Software",
    "Internet Services & Infrastructure",
    "IT Consulting & Other Services",
    "Data Processing & Outsourced Services",
}

_WIKI_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; SoftwareAnalyzer/1.0)"}


def _fetch_sp500_software() -> pd.DataFrame:
    """Fetch S&P 500 companies and filter to software sub-industries."""
    try:
        resp = requests.get(_WIKI_URL, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
        tables = pd.read_html(StringIO(resp.text))
        sp500 = tables[0]
        mask = sp500["GICS Sub-Industry"].isin(_SP500_SOFTWARE_SUBINDUSTRIES)
        filtered = sp500[mask][["Symbol", "Security", "GICS Sub-Industry"]].copy()
        filtered.columns = ["ticker", "name_en", "sub_industry"]
        filtered["source"] = "S&P 500"
        logger.info("Fetched %d software companies from S&P 500", len(filtered))
        return filtered
    except Exception as exc:
        logger.warning("Could not fetch S&P 500 list: %s", exc)
        return pd.DataFrame(columns=["ticker", "name_en", "sub_industry", "source"])


def build_universe(include_etfs: bool = True) -> pd.DataFrame:
    """
    Return a deduplicated DataFrame of all software-sector companies.

    Columns: ticker, name_en, sub_industry, category, source
    """
    sp500_df = _fetch_sp500_software()

    supp_rows = []
    for ticker, meta in SUPPLEMENTARY.items():
        if not include_etfs and meta["sub_industry"] == "ETF":
            continue
        supp_rows.append(
            {
                "ticker": ticker,
                "name_en": meta["name_en"],
                "sub_industry": meta["sub_industry"],
                "source": "Supplementary",
            }
        )
    supp_df = pd.DataFrame(supp_rows)

    combined = pd.concat([sp500_df, supp_df], ignore_index=True)

    # De-duplicate: S&P 500 entries take precedence
    combined = combined.drop_duplicates(subset="ticker", keep="first")
    combined["sub_industry"] = combined.apply(
        lambda row: TICKER_SUBINDUSTRY_OVERRIDES.get(row["ticker"], row["sub_industry"]),
        axis=1,
    )

    # Map to category
    combined["category"] = combined["sub_industry"].map(
        SUBINDUSTRY_CATEGORY
    ).fillna("기타")

    combined.sort_values(["category", "ticker"], inplace=True)
    combined.reset_index(drop=True, inplace=True)

    logger.info("Universe built: %d total companies", len(combined))
    return combined


if __name__ == "__main__":
    df = build_universe()
    print(df.groupby("category").size())
    print(f"\nTotal: {len(df)} companies")
