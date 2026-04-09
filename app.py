"""
Software Stock Decline Analyzer — Streamlit Dashboard
"""

import time
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from analyzer import (
    decline_buckets,
    get_top_decliners,
    rank_by_decline,
    sector_summary,
    summary_stats,
)
from companies import COMPANIES, SECTOR_COLORS
from data_fetcher import fetch_history, get_data

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="소프트웨어 주식 하락 분석기",
    page_icon="📉",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .metric-card {
        background: #1e2130;
        border-radius: 10px;
        padding: 16px 20px;
        border: 1px solid #2d3147;
    }
    .decline-badge {
        font-size: 1.3rem;
        font-weight: 700;
    }
    .stDataFrame { font-size: 0.85rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.image(
        "https://img.icons8.com/color/96/combo-chart--v1.png",
        width=64,
    )
    st.title("소프트웨어 주식\n하락 분석기")
    st.caption("Software Stock Decline Analyzer")
    st.divider()

    page = st.radio(
        "페이지",
        ["📊 개요", "🏆 하락 랭킹", "🔍 종목 분석", "ℹ️ 정보"],
        label_visibility="collapsed",
    )

    st.divider()

    force_refresh = st.button("🔄 데이터 새로고침", use_container_width=True)
    st.caption("데이터는 30분마다 자동 갱신됩니다.")

    st.divider()
    st.markdown(
        "**분석 대상 종목**  \n"
        + "  \n".join(
            f"- **{t}** {m['name_kr']}"
            for t, m in COMPANIES.items()
        )
    )

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
@st.cache_data(ttl=1800, show_spinner=False)
def load_data(refresh_token: int) -> pd.DataFrame:
    return get_data(force_refresh=(refresh_token != 0))


if "refresh_token" not in st.session_state:
    st.session_state.refresh_token = 0

if force_refresh:
    st.session_state.refresh_token += 1
    st.cache_data.clear()

with st.spinner("시장 데이터 불러오는 중…"):
    df = load_data(st.session_state.refresh_token)

if df.empty:
    st.error("데이터를 불러올 수 없습니다. 잠시 후 다시 시도해 주세요.")
    st.stop()

# Show banner if we're showing snapshot (fallback) data
updated_at = df["updated_at"].iloc[0] if "updated_at" in df.columns else ""
if "스냅샷" in str(updated_at):
    st.warning(
        "⚠️ 실시간 시장 데이터를 불러올 수 없어 **2026-04-10 스냅샷 데이터**를 표시합니다. "
        "잠시 후 '🔄 데이터 새로고침'을 눌러 주세요.",
        icon="📸",
    )

stats = summary_stats(df)

# ---------------------------------------------------------------------------
# Helper: colour a price-change value
# ---------------------------------------------------------------------------
def colour_pct(val: float) -> str:
    if val < 0:
        return f"🔴 {val:+.2f}%"
    if val > 0:
        return f"🟢 {val:+.2f}%"
    return f"⚪ {val:+.2f}%"


# ============================================================
#  PAGE: 개요 (Overview)
# ============================================================
if page == "📊 개요":
    st.header("📊 소프트웨어 기업 주가 현황")

    updated = df["updated_at"].iloc[0] if "updated_at" in df.columns else "N/A"
    st.caption(f"마지막 업데이트: {updated} UTC")

    # KPI row
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("분석 종목 수", stats.get("total_companies", 0), help="추적 중인 종목 수")
    k2.metric(
        "평균 52주 고점 대비 하락",
        f"{stats.get('avg_decline_from_high', 0):.1f}%",
    )
    k3.metric(
        "오늘 하락 종목 비율",
        f"{stats.get('pct_down_today', 0):.0f}%",
    )
    k4.metric(
        "최대 일간 하락",
        f"{stats.get('biggest_day_drop_pct', 0):.2f}%",
        delta_color="inverse",
    )

    st.divider()

    # Main table
    st.subheader("전체 종목 현황")
    display_cols = {
        "ticker": "티커",
        "name_kr": "종목명 (한국어)",
        "name_en": "종목명 (영어)",
        "sector": "섹터",
        "current_price": "현재가",
        "day_change_pct": "당일 등락률",
        "high_52w": "52주 고점",
        "decline_from_high_pct": "고점 대비 하락률",
        "currency": "통화",
    }
    table_df = df[list(display_cols.keys())].rename(columns=display_cols).copy()
    table_df["당일 등락률"] = table_df["당일 등락률"].apply(lambda v: f"{v:+.2f}%")
    table_df["고점 대비 하락률"] = table_df["고점 대비 하락률"].apply(lambda v: f"{v:.2f}%")

    st.dataframe(table_df, use_container_width=True, hide_index=True)

    st.divider()

    # Two charts side by side
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("📉 52주 고점 대비 하락률")
        fig = px.bar(
            rank_by_decline(df),
            x="decline_from_high_pct",
            y="name_kr",
            orientation="h",
            color="sector",
            color_discrete_map=SECTOR_COLORS,
            labels={"decline_from_high_pct": "하락률 (%)", "name_kr": ""},
            text="decline_from_high_pct",
        )
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig.update_layout(
            height=520,
            margin=dict(l=0, r=60, t=20, b=20),
            showlegend=True,
            xaxis_title="하락률 (%)",
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("📅 당일 등락률")
        day_df = df.sort_values("day_change_pct", ascending=True)
        colors = ["#EF4444" if v < 0 else "#10B981" for v in day_df["day_change_pct"]]
        fig2 = go.Figure(
            go.Bar(
                x=day_df["day_change_pct"],
                y=day_df["name_kr"],
                orientation="h",
                marker_color=colors,
                text=day_df["day_change_pct"].apply(lambda v: f"{v:+.2f}%"),
                textposition="outside",
            )
        )
        fig2.update_layout(
            height=520,
            margin=dict(l=0, r=60, t=20, b=20),
            xaxis_title="등락률 (%)",
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Sector heatmap
    st.subheader("🗂️ 섹터별 평균 하락률")
    sec_df = sector_summary(df)
    fig3 = px.bar(
        sec_df,
        x="sector",
        y="avg_decline",
        color="avg_decline",
        color_continuous_scale="RdYlGn",
        text="avg_decline",
        labels={"avg_decline": "평균 하락률 (%)", "sector": "섹터"},
    )
    fig3.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig3.update_layout(coloraxis_showscale=False, height=380)
    st.plotly_chart(fig3, use_container_width=True)


# ============================================================
#  PAGE: 하락 랭킹
# ============================================================
elif page == "🏆 하락 랭킹":
    st.header("🏆 52주 고점 대비 하락 랭킹")
    st.caption("52주 최고가 대비 현재 주가의 하락폭 기준 정렬")

    top_n = st.slider("표시할 종목 수", min_value=5, max_value=len(df), value=min(10, len(df)))

    ranked = rank_by_decline(df).head(top_n).reset_index(drop=True)
    ranked.index += 1

    for i, row in ranked.iterrows():
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([0.5, 2.5, 1.5, 1.5, 1.5])
            col1.markdown(f"**#{i}**")
            col2.markdown(f"**{row['name_kr']}**  \n`{row['ticker']}` · {row['sector']}")
            col3.metric("현재가", f"{row['current_price']:,.4f} {row.get('currency','USD')}")
            col4.metric("당일 등락", colour_pct(row["day_change_pct"]))
            col5.metric(
                "52주 고점 대비",
                f"{row['decline_from_high_pct']:.2f}%",
                delta=f"고점: {row['high_52w']:,.2f}",
                delta_color="off",
            )
        st.divider()

    # Bucket chart
    st.subheader("📦 하락 구간별 분포")
    bucket_df = decline_buckets(df)
    fig = px.pie(
        bucket_df,
        values="count",
        names="bucket",
        color_discrete_sequence=px.colors.sequential.RdBu_r,
        hole=0.4,
    )
    fig.update_layout(height=380)
    st.plotly_chart(fig, use_container_width=True)


# ============================================================
#  PAGE: 종목 분석
# ============================================================
elif page == "🔍 종목 분석":
    st.header("🔍 종목 상세 분석")

    ticker_options = df["ticker"].tolist()
    names = [f"{t} — {COMPANIES.get(t, {}).get('name_kr', t)}" for t in ticker_options]
    selected_label = st.selectbox("종목 선택", names)
    selected_ticker = selected_label.split(" — ")[0]

    row = df[df["ticker"] == selected_ticker].iloc[0]

    st.subheader(f"{row['name_kr']}  ({selected_ticker})")
    st.caption(f"{row['name_en']} · {row['sector']} · {row.get('exchange','')}")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("현재가", f"{row['current_price']:,.4f}", f"{row['day_change']:+,.4f}")
    m2.metric("당일 등락률", f"{row['day_change_pct']:+.2f}%")
    m3.metric("52주 고점", f"{row['high_52w']:,.4f}")
    m4.metric("52주 고점 대비 하락", f"{row['decline_from_high_pct']:.2f}%")

    m5, m6, m7 = st.columns(3)
    m5.metric("52주 저점", f"{row['low_52w']:,.4f}")
    m6.metric("전일 종가", f"{row['prev_close']:,.4f}")
    if row.get("market_cap"):
        m7.metric("시가총액", f"${row['market_cap']:,.0f}")

    st.divider()

    period = st.select_slider(
        "기간 선택",
        options=["1mo", "3mo", "6mo", "1y"],
        value="1y",
        format_func=lambda x: {"1mo": "1개월", "3mo": "3개월", "6mo": "6개월", "1y": "1년"}[x],
    )

    with st.spinner("차트 데이터 로딩 중…"):
        hist = fetch_history(selected_ticker, period=period)

    if hist.empty:
        st.warning("이 종목의 과거 데이터를 불러올 수 없습니다.")
    else:
        # Candlestick
        fig_candle = go.Figure(
            go.Candlestick(
                x=hist.index,
                open=hist["Open"],
                high=hist["High"],
                low=hist["Low"],
                close=hist["Close"],
                name=selected_ticker,
                increasing_line_color="#10B981",
                decreasing_line_color="#EF4444",
            )
        )
        # 52W high line
        fig_candle.add_hline(
            y=row["high_52w"],
            line_dash="dash",
            line_color="#F59E0B",
            annotation_text=f"52주 고점 {row['high_52w']:,.2f}",
            annotation_position="bottom right",
        )
        fig_candle.update_layout(
            title=f"{row['name_kr']} — 주가 차트",
            height=450,
            xaxis_rangeslider_visible=False,
            xaxis_title="날짜",
            yaxis_title=f"주가 ({row.get('currency','USD')})",
        )
        st.plotly_chart(fig_candle, use_container_width=True)

        # Volume bar
        fig_vol = px.bar(
            x=hist.index,
            y=hist["Volume"],
            labels={"x": "날짜", "y": "거래량"},
            title="거래량",
            color_discrete_sequence=["#3B82F6"],
        )
        fig_vol.update_layout(height=220)
        st.plotly_chart(fig_vol, use_container_width=True)

        # Returns
        hist["daily_return"] = hist["Close"].pct_change() * 100
        fig_ret = px.area(
            x=hist.index,
            y=hist["daily_return"],
            labels={"x": "날짜", "y": "일간 수익률 (%)"},
            title="일간 수익률 분포",
            color_discrete_sequence=["#8B5CF6"],
        )
        fig_ret.update_layout(height=220)
        st.plotly_chart(fig_ret, use_container_width=True)


# ============================================================
#  PAGE: 정보
# ============================================================
elif page == "ℹ️ 정보":
    st.header("ℹ️ 앱 소개")
    st.markdown(
        """
## 소프트웨어 주식 하락 분석기

이 애플리케이션은 글로벌 주요 **소프트웨어 / 핀테크 / AI / 사이버보안** 기업들의 주가 하락 현황을 추적하고 시각화합니다.

### 주요 기능
| 기능 | 설명 |
|------|------|
| 📊 개요 | 전 종목 가격 현황 및 섹터 요약 |
| 🏆 하락 랭킹 | 52주 고점 대비 하락폭 순위 |
| 🔍 종목 분석 | 캔들차트·거래량·일간 수익률 상세 분석 |
| 🔄 자동 갱신 | 30분 단위 캐시 자동 갱신 |

### 추적 종목 (18종)
        """
    )

    for ticker, meta in COMPANIES.items():
        st.markdown(
            f"- **`{ticker}`** &nbsp; {meta['name_kr']} &nbsp; ({meta['name_en']}) &nbsp; "
            f"— *{meta['sector']}* · {meta['exchange']}"
        )

    st.markdown(
        """
### 기술 스택
- **Python 3.11+**
- **yfinance** — 주가 데이터 수집
- **Streamlit** — 웹 대시보드
- **Plotly** — 인터랙티브 차트
- **Pandas / NumPy** — 데이터 처리
- **SQLite / CSV** — 로컬 캐시

### 데이터 출처
Yahoo Finance (yfinance 라이브러리) 공개 API를 통해 수집합니다.
실시간 데이터가 아닐 수 있으며, 투자 결정에 직접 활용하지 마십시오.
        """
    )
