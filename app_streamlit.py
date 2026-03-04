"""
WhaleWatch Alpha — Streamlit Dashboard
Real NSE data | 4 Universe Toggles | 7-Factor Ranking
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent))

from src.data.universe_builder import build_real_universe, UNIVERSE_MAP
from src.pipeline.daily_alpha_pipeline import run_pipeline

st.set_page_config(page_title="WhaleWatch Alpha", page_icon="🐋", layout="wide")

st.title("🐋 WhaleWatch Alpha")
st.caption(f"NSE Multi-Factor Daily Stock Ranking Engine  •  {date.today().strftime('%d %b %Y')}")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")

    universe = st.radio(
        "📊 Stock Universe",
        options=list(UNIVERSE_MAP.keys()),
        index=0,
        help="Nifty 100 = fastest | All NSE = most comprehensive",
    )

    universe_sizes = {
        "Nifty 100":  "~100 stocks • ~1 min",
        "F&O Stocks": "~90 stocks  • ~1 min",
        "Nifty 500":  "~250 stocks • ~3 min",
        "All NSE":    "~300+ stocks • ~4 min",
    }
    st.caption(universe_sizes.get(universe, ""))

    top_n = st.slider("Top N Stocks", 5, 20, 10)

    st.divider()
    st.markdown("**Factor Weights**")
    st.markdown("""
| Factor | Weight |
|--------|--------|
| Technical | 25% |
| Valuation | 20% |
| Moat | 15% |
| Quant | 15% |
| Macro | 10% |
| Risk (inv) | 10% |
| Whale | 5% |
    """)
    run_btn = st.button("🔄 Run Pipeline", use_container_width=True, type="primary")

# ── Session state ─────────────────────────────────────────────────────────────
if "results" not in st.session_state:
    st.session_state.results   = None
    st.session_state.universe  = None
    st.session_state.hist_data = {}

# ── Run pipeline ──────────────────────────────────────────────────────────────
if run_btn or st.session_state.results is None:
    with st.spinner(f"📡 Fetching {universe} data from Yahoo Finance..."):
        universe_df = build_real_universe(universe=universe)

    if universe_df.empty:
        st.error("No data fetched. Check your internet connection and try again.")
        st.stop()

    with st.spinner("⚙️ Running 7-factor alpha pipeline..."):
        results = run_pipeline(universe_df, top_n=top_n)
        st.session_state.hist_data = {
            row["symbol"]: universe_df[
                universe_df["symbol"] == row["symbol"]
            ]["price_df"].values[0]
            for _, row in results.iterrows()
            if row["symbol"] in universe_df["symbol"].values
        }
        st.session_state.results  = results
        st.session_state.universe = universe

    days = max(
        [len(v) for v in st.session_state.hist_data.values() if v is not None],
        default=0,
    )
    st.success(
        f"✅ {universe} pipeline complete — "
        f"{len(universe_df)} stocks scanned | "
        f"Top {top_n} ranked | "
        f"📅 {days} trading days of history"
    )

df = st.session_state.results
if df is None or df.empty:
    st.info("👈 Click **Run Pipeline** in the sidebar to start.")
    st.stop()

# ── KPI row ───────────────────────────────────────────────────────────────────
st.divider()
c1,c2,c3,c4 = st.columns(4)
c1.metric("🏆 Top Stock",     df["symbol"].iloc[0])
c2.metric("⭐ Best Score",    f"{df['final_score'].iloc[0]:.4f}")
c3.metric("📊 Avg Score",     f"{df['final_score'].mean():.4f}")
c4.metric("🔭 Universe",      st.session_state.universe or universe)
st.divider()

# ── Table ─────────────────────────────────────────────────────────────────────
st.subheader("📋 Top Alpha Stocks")
score_cols = ["final_score","technical","valuation","moat","quant","macro","risk","whale"]
display_df = df.copy()
for c in score_cols:
    if c in display_df.columns:
        display_df[c] = display_df[c].apply(lambda x: round(float(x), 4))

st.dataframe(display_df, use_container_width=True, height=420)

csv_data = display_df.to_csv(index=False).encode("utf-8")
st.download_button("📥 Download CSV", csv_data, "alpha_top10.csv", "text/csv")

st.divider()

# ── Bar + Radar ───────────────────────────────────────────────────────────────
cl, cr = st.columns(2)

with cl:
    st.subheader("🎯 Final Alpha Score")
    fig_bar = px.bar(
        df.sort_values("final_score"),
        x="final_score", y="symbol", orientation="h",
        color="final_score", color_continuous_scale="Teal",
        labels={"final_score":"Alpha Score","symbol":"Stock"},
    )
    fig_bar.update_layout(showlegend=False, coloraxis_showscale=False,
                          height=420, margin=dict(l=10,r=10,t=10,b=10))
    st.plotly_chart(fig_bar, use_container_width=True)

with cr:
    st.subheader("📡 Factor Breakdown — Top Stock")
    top_stock = df.iloc[0]
    fcols     = [c for c in ["technical","valuation","moat","quant","macro","whale"] if c in df.columns]
    fvals     = [float(top_stock[c]) for c in fcols]
    fig_radar = go.Figure(go.Scatterpolar(
        r=fvals+[fvals[0]], theta=fcols+[fcols[0]],
        fill="toself", fillcolor="rgba(0,180,180,0.2)",
        line=dict(color="teal", width=2),
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0,1])),
        showlegend=False, height=420, margin=dict(l=40,r=40,t=40,b=40),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

# ── Price history ─────────────────────────────────────────────────────────────
st.divider()
st.subheader("📈 Price History — Top 10 Stocks (Indexed, Base = 100)")

hist_data = st.session_state.hist_data
if hist_data:
    fig_hist = go.Figure()
    for symbol, price_df in hist_data.items():
        if price_df is not None and len(price_df) >= 5:
            pdf   = price_df.copy().reset_index()
            pdf["norm"] = pdf["close"] / pdf["close"].iloc[0] * 100
            xcol  = "Date" if "Date" in pdf.columns else pdf.columns[0]
            fig_hist.add_trace(go.Scatter(
                x=pdf[xcol], y=pdf["norm"],
                mode="lines", name=symbol, line=dict(width=1.8),
                hovertemplate="%{y:.1f}<extra>%{fullData.name}</extra>",
            ))
    fig_hist.update_layout(
        height=460,
        xaxis_title="Date",
        yaxis_title="Indexed Price (Base=100)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        margin=dict(l=10,r=10,t=40,b=10),
        hovermode="x unified",
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    days = max([len(v) for v in hist_data.values() if v is not None], default=0)
    st.caption(
        f"📅 {days} trading days available today. "
        "Data window grows automatically — more history every day."
    )

# ── Heatmap ───────────────────────────────────────────────────────────────────
st.divider()
st.subheader("🔥 Factor Heatmap — All Ranked Stocks")
hcols   = [c for c in ["technical","valuation","moat","quant","macro","whale"] if c in df.columns]
heat_df = df[["symbol"]+hcols].set_index("symbol").astype(float)
fig_heat = px.imshow(
    heat_df, color_continuous_scale="RdYlGn", aspect="auto",
    labels=dict(x="Factor",y="Stock",color="Score"), zmin=0, zmax=1,
)
fig_heat.update_layout(height=420, margin=dict(l=10,r=10,t=10,b=10))
st.plotly_chart(fig_heat, use_container_width=True)

st.caption("WhaleWatch Alpha | Data: Yahoo Finance NSE | Refresh daily for latest rankings")
