"""
전체 소프트웨어 섹터 주가 하락 분석기
Software Sector Decline Analyzer — Full Universe Streamlit Dashboard
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from analyzer import (
    category_summary,
    decline_distribution,
    get_top_decliners,
    rank_by_decline,
    rank_by_day_change,
    sub_industry_summary,
    summary_stats,
)
from data_fetcher import fetch_history, get_data

# ─────────────────────────────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="소프트웨어 섹터 하락 분석기",
    page_icon="📉",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
[data-testid="stMetricValue"] { font-size: 1.15rem !important; }
[data-testid="stMetricLabel"] { font-size: 0.78rem !important; color: #9ca3af; }
.stDataFrame { font-size: 0.82rem; }
div[data-testid="column"] { padding: 0 4px; }
</style>
""", unsafe_allow_html=True)

# Category colours
CAT_COLORS = {
    "애플리케이션 소프트웨어":     "#3B82F6",
    "시스템 소프트웨어 / 보안":    "#EF4444",
    "인터넷 / 클라우드 인프라":    "#10B981",
    "IT 컨설팅 / 서비스":         "#F59E0B",
    "데이터 처리 / 아웃소싱":      "#8B5CF6",
    "ETF":                        "#6B7280",
    "기타":                        "#9CA3AF",
}

# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📉 소프트웨어 섹터\n### 하락 분석기")
    st.caption("Software Sector Decline Analyzer")
    st.divider()

    page = st.radio(
        "페이지",
        ["📊 전체 개요", "🏆 하락 랭킹", "🗂️ 섹터 분석", "🔍 종목 상세", "ℹ️ 정보"],
        label_visibility="collapsed",
    )
    st.divider()

    refresh_btn = st.button("🔄 데이터 새로고침", use_container_width=True)
    st.caption("캐시 유효시간: 30분")
    st.divider()

    # Category filter (multi-select)
    all_categories = list(CAT_COLORS.keys())
    selected_cats = st.multiselect(
        "카테고리 필터",
        options=all_categories,
        default=all_categories,
        help="표시할 카테고리를 선택하세요",
    )

    # ETF toggle
    show_etf = "ETF" in selected_cats

# ─────────────────────────────────────────────────────────────────────────────
# Data loading
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=1800, show_spinner=False)
def load(token: int) -> pd.DataFrame:
    return get_data(force_refresh=(token != 0))

if "token" not in st.session_state:
    st.session_state.token = 0
if refresh_btn:
    st.session_state.token += 1
    st.cache_data.clear()

with st.spinner("📡 전체 소프트웨어 섹터 데이터 수집 중…"):
    raw_df = load(st.session_state.token)

if raw_df.empty:
    st.error("데이터를 불러올 수 없습니다.")
    st.stop()

# Snapshot banner
if "스냅샷" in str(raw_df.get("updated_at", pd.Series([""])).iloc[0]):
    st.warning("⚠️ 실시간 데이터 수집 실패 — 스냅샷 데이터를 표시합니다. '🔄 새로고침'을 눌러보세요.", icon="📸")

# Apply category filter
df = raw_df[raw_df["category"].isin(selected_cats)].copy() if selected_cats else raw_df.copy()

stats = summary_stats(df)
updated_at = raw_df["updated_at"].iloc[0] if "updated_at" in raw_df.columns else "N/A"


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def pct_arrow(val: float) -> str:
    if pd.isna(val):
        return "—"
    arrow = "▼" if val < 0 else "▲" if val > 0 else "─"
    colour = "red" if val < 0 else "green" if val > 0 else "gray"
    return f'<span style="color:{colour}">{arrow} {abs(val):.2f}%</span>'


def make_bar_chart(data: pd.DataFrame, x_col: str, y_col: str,
                   color_col: str | None = None, title: str = "",
                   height: int = 500) -> go.Figure:
    color_map = CAT_COLORS if color_col == "category" else None
    fig = px.bar(
        data, x=x_col, y=y_col, orientation="h",
        color=color_col, color_discrete_map=color_map,
        text=x_col, title=title,
        labels={x_col: "", y_col: ""},
        height=height,
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(margin=dict(l=0, r=70, t=30, b=10),
                      showlegend=bool(color_col), legend_title_text="")
    return fig


# ═════════════════════════════════════════════════════════════════════════════
# PAGE: 전체 개요
# ═════════════════════════════════════════════════════════════════════════════
if page == "📊 전체 개요":
    st.header("📊 전체 소프트웨어 섹터 현황")
    st.caption(f"마지막 업데이트: {updated_at} | 총 **{stats.get('total', 0)}개** 종목")

    # ── KPI row ──────────────────────────────────────────────────────────────
    k = st.columns(5)
    k[0].metric("추적 종목 수",        f"{stats.get('total', 0)}개")
    k[1].metric("평균 52주 고점 대비",  f"{stats.get('avg_decline', 0):.1f}%")
    k[2].metric("중간값 하락률",        f"{stats.get('median_decline', 0):.1f}%")
    k[3].metric("오늘 하락 비율",       f"{stats.get('pct_down_today', 0):.0f}%")
    k[4].metric("30%+ 하락 종목 비율",  f"{stats.get('pct_down_30_from_high', 0):.0f}%")

    st.divider()

    # ── 최대 하락 / 당일 최대 낙폭 ──────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🔻 52주 최대 하락",
              stats.get("worst_ticker", ""),
              f"{stats.get('worst_decline', 0):.1f}%  ({stats.get('worst_name', '')})",
              delta_color="inverse")
    c2.metric("📈 52주 최소 하락",
              stats.get("best_ticker", ""),
              f"{stats.get('best_decline', 0):.1f}%  ({stats.get('best_name', '')})")
    c3.metric("🔴 당일 최대 하락",
              stats.get("day_drop_ticker", ""),
              f"{stats.get('day_drop_pct', 0):.2f}%  ({stats.get('day_drop_name', '')})",
              delta_color="inverse")
    c4.metric("🟢 당일 최대 상승",
              stats.get("day_gain_ticker", ""),
              f"{stats.get('day_gain_pct', 0):.2f}%  ({stats.get('day_gain_name', '')})")

    st.divider()

    # ── Full table ────────────────────────────────────────────────────────────
    st.subheader("전체 종목 테이블")

    search = st.text_input("🔍 종목 검색 (티커 / 회사명)", placeholder="CRWD, Salesforce …")
    if search:
        mask = (
            df["ticker"].str.upper().str.contains(search.upper(), na=False) |
            df["name_en"].str.upper().str.contains(search.upper(), na=False)
        )
        show_df = df[mask]
    else:
        show_df = df

    display = show_df[[
        "ticker", "name_en", "category", "sub_industry",
        "current_price", "currency",
        "day_change_pct", "high_52w", "decline_from_high_pct",
    ]].rename(columns={
        "ticker":                "티커",
        "name_en":               "회사명",
        "category":              "카테고리",
        "sub_industry":          "세부 업종",
        "current_price":         "현재가",
        "currency":              "통화",
        "day_change_pct":        "당일 등락률(%)",
        "high_52w":              "52주 고점",
        "decline_from_high_pct": "고점 대비 하락률(%)",
    }).sort_values("고점 대비 하락률(%)", ascending=True)

    st.dataframe(
        display.style
        .background_gradient(subset=["고점 대비 하락률(%)"], cmap="RdYlGn")
        .background_gradient(subset=["당일 등락률(%)"], cmap="RdYlGn"),
        use_container_width=True, hide_index=True,
    )

    st.divider()

    # ── Charts row ────────────────────────────────────────────────────────────
    ch1, ch2 = st.columns(2)

    with ch1:
        st.subheader("📉 52주 고점 대비 하락률 (전체)")
        ranked = rank_by_decline(df)
        fig = px.bar(
            ranked, x="decline_from_high_pct", y="ticker",
            orientation="h", color="category",
            color_discrete_map=CAT_COLORS,
            text="decline_from_high_pct",
            labels={"decline_from_high_pct": "하락률(%)", "ticker": ""},
            height=max(400, len(ranked) * 18),
        )
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig.update_layout(margin=dict(l=0, r=60, t=10, b=10), showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

    with ch2:
        st.subheader("📅 당일 등락률")
        day_sorted = rank_by_day_change(df)
        colors = ["#EF4444" if v < 0 else "#10B981" for v in day_sorted["day_change_pct"]]
        fig2 = go.Figure(go.Bar(
            x=day_sorted["day_change_pct"],
            y=day_sorted["ticker"],
            orientation="h",
            marker_color=colors,
            text=day_sorted["day_change_pct"].apply(lambda v: f"{v:+.2f}%"),
            textposition="outside",
        ))
        fig2.update_layout(
            height=max(400, len(day_sorted) * 18),
            margin=dict(l=0, r=60, t=10, b=10),
            xaxis_title="등락률(%)",
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Scatter: decline vs day change ────────────────────────────────────────
    st.subheader("🔵 52주 고점 대비 하락률 vs 당일 등락률")
    fig_sc = px.scatter(
        df.dropna(subset=["decline_from_high_pct", "day_change_pct"]),
        x="decline_from_high_pct", y="day_change_pct",
        color="category", color_discrete_map=CAT_COLORS,
        size_max=20,
        hover_data=["ticker", "name_en", "current_price"],
        labels={"decline_from_high_pct": "52주 고점 대비 하락률(%)",
                "day_change_pct": "당일 등락률(%)"},
        text="ticker",
        height=500,
    )
    fig_sc.update_traces(textposition="top center", textfont_size=9)
    fig_sc.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    fig_sc.add_vline(x=df["decline_from_high_pct"].mean(),
                     line_dash="dash", line_color="orange", opacity=0.5,
                     annotation_text="평균 하락선")
    st.plotly_chart(fig_sc, use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE: 하락 랭킹
# ═════════════════════════════════════════════════════════════════════════════
elif page == "🏆 하락 랭킹":
    st.header("🏆 52주 고점 대비 하락 랭킹")

    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
        top_n = st.slider("표시 종목 수", 10, len(df), min(30, len(df)))
    with col_f2:
        sort_by = st.selectbox("정렬 기준",
                               ["52주 고점 대비 하락률", "당일 등락률"])

    if sort_by == "당일 등락률":
        ranked = rank_by_day_change(df).head(top_n)
        val_col, label = "day_change_pct", "당일 등락률"
    else:
        ranked = rank_by_decline(df).head(top_n)
        val_col, label = "decline_from_high_pct", "52주 고점 대비 하락률"

    # Card-style list
    for rank_i, (_, row) in enumerate(ranked.iterrows(), 1):
        with st.container(border=True):
            c1, c2, c3, c4, c5 = st.columns([0.5, 3, 1.5, 1.5, 1.5])
            c1.markdown(f"**#{rank_i}**")
            c2.markdown(
                f"**{row['ticker']}**  \n"
                f"{row['name_en']}  \n"
                f"<small style='color:#9ca3af'>{row['category']} · {row['sub_industry']}</small>",
                unsafe_allow_html=True,
            )
            c3.metric("현재가", f"{row['current_price']:,.2f} {row.get('currency','USD')}")
            c4.metric("당일 등락", f"{row['day_change_pct']:+.2f}%")
            c5.metric("52주 고점 대비", f"{row['decline_from_high_pct']:.2f}%",
                      help=f"52주 고점: {row['high_52w']:,.2f}")

    st.divider()

    # Distribution buckets
    st.subheader("📊 하락 구간 분포")
    bucket_df = decline_distribution(df)
    fig_bkt = px.bar(
        bucket_df, x="bucket", y="종목수",
        color="bucket",
        color_discrete_sequence=px.colors.diverging.RdYlGn[::-1],
        text="종목수",
        labels={"bucket": "하락 구간", "종목수": "종목 수"},
        height=350,
    )
    fig_bkt.update_traces(textposition="outside")
    fig_bkt.update_layout(showlegend=False, xaxis_title="", yaxis_title="종목 수")
    st.plotly_chart(fig_bkt, use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE: 섹터 분석
# ═════════════════════════════════════════════════════════════════════════════
elif page == "🗂️ 섹터 분석":
    st.header("🗂️ 카테고리 / 섹터별 분석")

    # ── Category treemap ─────────────────────────────────────────────────────
    st.subheader("🌳 카테고리별 종목 분포 (Treemap)")
    tree_df = df.dropna(subset=["decline_from_high_pct"]).copy()
    tree_df["size"] = 1
    fig_tree = px.treemap(
        tree_df,
        path=["category", "ticker"],
        values="size",
        color="decline_from_high_pct",
        color_continuous_scale="RdYlGn",
        color_continuous_midpoint=tree_df["decline_from_high_pct"].median(),
        hover_data=["name_en", "current_price", "day_change_pct"],
        title="색상: 52주 고점 대비 하락률 (초록=양호, 빨강=큰 하락)",
        height=550,
    )
    st.plotly_chart(fig_tree, use_container_width=True)

    st.divider()

    # ── Category bar ─────────────────────────────────────────────────────────
    cat_df = category_summary(df)
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("카테고리별 평균 52주 하락률")
        fig_cat = px.bar(
            cat_df, x="평균하락률", y="category",
            orientation="h", color="평균하락률",
            color_continuous_scale="RdYlGn",
            text="평균하락률",
            labels={"평균하락률": "평균 하락률(%)", "category": ""},
            height=380,
        )
        fig_cat.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_cat.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_cat, use_container_width=True)

    with col2:
        st.subheader("카테고리별 당일 평균 등락률")
        fig_day = px.bar(
            cat_df, x="당일평균등락", y="category",
            orientation="h", color="당일평균등락",
            color_continuous_scale="RdYlGn",
            color_continuous_midpoint=0,
            text="당일평균등락",
            labels={"당일평균등락": "평균 등락률(%)", "category": ""},
            height=380,
        )
        fig_day.update_traces(texttemplate="%{text:+.2f}%", textposition="outside")
        fig_day.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_day, use_container_width=True)

    # ── Sub-industry table ────────────────────────────────────────────────────
    st.subheader("세부 업종별 요약")
    sub_df = sub_industry_summary(df)
    st.dataframe(
        sub_df.style.background_gradient(subset=["평균하락률"], cmap="RdYlGn"),
        use_container_width=True, hide_index=True,
    )

    # ── Category detail tables ────────────────────────────────────────────────
    st.subheader("카테고리별 종목 현황")
    for cat in sorted(df["category"].unique()):
        cat_data = df[df["category"] == cat].sort_values("decline_from_high_pct")
        with st.expander(f"{cat}  ({len(cat_data)}개 종목)", expanded=False):
            st.dataframe(
                cat_data[[
                    "ticker", "name_en", "current_price", "currency",
                    "day_change_pct", "high_52w", "decline_from_high_pct",
                ]].rename(columns={
                    "ticker":                "티커",
                    "name_en":               "회사명",
                    "current_price":         "현재가",
                    "currency":              "통화",
                    "day_change_pct":        "당일(%)",
                    "high_52w":              "52주 고점",
                    "decline_from_high_pct": "고점 대비(%)",
                }).style.background_gradient(subset=["고점 대비(%)"], cmap="RdYlGn"),
                use_container_width=True, hide_index=True,
            )


# ═════════════════════════════════════════════════════════════════════════════
# PAGE: 종목 상세
# ═════════════════════════════════════════════════════════════════════════════
elif page == "🔍 종목 상세":
    st.header("🔍 종목 상세 분석")

    options = [f"{r['ticker']} — {r['name_en']}" for _, r in df.iterrows()]
    sel_label = st.selectbox("종목 선택", sorted(options))
    sel_ticker = sel_label.split(" — ")[0]
    row = df[df["ticker"] == sel_ticker].iloc[0]

    st.subheader(f"{row['ticker']}  |  {row['name_en']}")
    st.caption(f"{row['category']}  ·  {row['sub_industry']}")

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("현재가",       f"{row['current_price']:,.4f} {row.get('currency','USD')}",
              f"{row['day_change']:+,.4f}")
    m2.metric("당일 등락률",   f"{row['day_change_pct']:+.2f}%")
    m3.metric("52주 고점",    f"{row['high_52w']:,.2f}")
    m4.metric("52주 저점",    f"{row['low_52w']:,.2f}")
    m5.metric("고점 대비 하락", f"{row['decline_from_high_pct']:.2f}%")

    if row.get("market_cap"):
        st.caption(f"시가총액: ${row['market_cap']:,.0f}")

    st.divider()

    period = st.select_slider(
        "조회 기간",
        ["1mo", "3mo", "6mo", "1y"],
        value="1y",
        format_func=lambda x: {"1mo":"1개월","3mo":"3개월","6mo":"6개월","1y":"1년"}[x],
    )

    with st.spinner("차트 데이터 로딩…"):
        hist = fetch_history(sel_ticker, period=period)

    if hist.empty:
        st.warning("차트 데이터를 불러올 수 없습니다.")
    else:
        # Candlestick
        fig_c = go.Figure(go.Candlestick(
            x=hist.index, open=hist["Open"], high=hist["High"],
            low=hist["Low"],  close=hist["Close"],
            increasing_line_color="#10B981",
            decreasing_line_color="#EF4444",
            name=sel_ticker,
        ))
        fig_c.add_hline(
            y=row["high_52w"], line_dash="dash", line_color="#F59E0B",
            annotation_text=f"52주 고점 {row['high_52w']:,.2f}",
        )
        fig_c.update_layout(
            title=f"{row['name_en']} 주가 차트",
            height=420, xaxis_rangeslider_visible=False,
            xaxis_title="날짜", yaxis_title=f"주가 ({row.get('currency','USD')})",
        )
        st.plotly_chart(fig_c, use_container_width=True)

        # Volume + daily return side by side
        v1, v2 = st.columns(2)
        with v1:
            fig_vol = px.bar(x=hist.index, y=hist["Volume"],
                             title="거래량", height=220,
                             color_discrete_sequence=["#3B82F6"],
                             labels={"x":"날짜","y":"거래량"})
            fig_vol.update_layout(showlegend=False)
            st.plotly_chart(fig_vol, use_container_width=True)

        with v2:
            ret = hist["Close"].pct_change() * 100
            fig_ret = px.area(
                x=hist.index, y=ret,
                title="일간 수익률(%)", height=220,
                color_discrete_sequence=["#8B5CF6"],
                labels={"x":"날짜","y":"수익률(%)"},
            )
            st.plotly_chart(fig_ret, use_container_width=True)

        # Performance vs category average
        st.subheader("동일 카테고리 대비 상대 성과")
        cat_peers = df[df["category"] == row["category"]].sort_values("decline_from_high_pct")
        fig_peer = px.bar(
            cat_peers, x="decline_from_high_pct", y="ticker",
            orientation="h",
            color=cat_peers["ticker"].apply(lambda t: "선택 종목" if t == sel_ticker else "동일 카테고리"),
            color_discrete_map={"선택 종목": "#F59E0B", "동일 카테고리": "#3B82F6"},
            text="decline_from_high_pct",
            labels={"decline_from_high_pct":"고점 대비 하락률(%)","ticker":""},
            height=max(300, len(cat_peers) * 24),
        )
        fig_peer.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_peer.update_layout(showlegend=True, margin=dict(l=0, r=60, t=10, b=10))
        st.plotly_chart(fig_peer, use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE: 정보
# ═════════════════════════════════════════════════════════════════════════════
elif page == "ℹ️ 정보":
    st.header("ℹ️ 앱 소개")
    st.markdown(f"""
## 전체 소프트웨어 섹터 주가 하락 분석기

S&P 500 및 주요 소프트웨어 기업 **{stats.get('total', '100+')}개 종목**을 추적하는 종합 대시보드입니다.

### 데이터 소스
| 소스 | 내용 |
|------|------|
| Wikipedia S&P 500 | Application Software, Systems Software, Internet Services & Infrastructure, IT Consulting 등 자동 수집 |
| 보조 종목 리스트 | S&P 500 外 주요 소프트웨어 기업 (Snowflake, Zscaler, GitLab 등) 수동 추가 |
| Yahoo Finance | yfinance 라이브러리를 통한 실시간 주가 데이터 |

### 카테고리 분류
| 카테고리 | 설명 |
|----------|------|
| 애플리케이션 소프트웨어 | SaaS, ERP, CRM, AI 소프트웨어 등 |
| 시스템 소프트웨어 / 보안 | OS, 사이버보안, 네트워크 보안 |
| 인터넷 / 클라우드 인프라 | CDN, 클라우드 플랫폼, 도메인 서비스 |
| IT 컨설팅 / 서비스 | IT 아웃소싱, 컨설팅, 관리 서비스 |
| 데이터 처리 / 아웃소싱 | 데이터 처리, BPO 서비스 |
| ETF | 소프트웨어 섹터 상장지수펀드 |

### 주요 기능
- 📊 **전체 개요** — 전 종목 현황 테이블 + 검색 + 산점도
- 🏆 **하락 랭킹** — 52주 고점 대비 하락폭 순위 카드 뷰
- 🗂️ **섹터 분석** — Treemap + 카테고리별 집계
- 🔍 **종목 상세** — 캔들차트, 거래량, 동료 비교
- 🔄 30분 단위 자동 캐시 갱신

### 기술 스택
`Python 3.11` · `yfinance` · `Streamlit` · `Plotly` · `Pandas` · `SQLite`

> **⚠️ 면책 고지**: 이 앱의 데이터는 투자 조언이 아닙니다. 모든 투자 결정은 본인 책임 하에 이루어져야 합니다.
""")

    if st.checkbox("현재 추적 중인 전체 종목 목록 보기"):
        st.dataframe(
            df[["ticker", "name_en", "category", "sub_industry", "source"]].rename(columns={
                "ticker": "티커", "name_en": "회사명",
                "category": "카테고리", "sub_industry": "세부 업종", "source": "출처",
            }),
            use_container_width=True, hide_index=True,
        )
