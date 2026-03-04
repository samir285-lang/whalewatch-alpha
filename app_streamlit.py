"""
WhaleWatch Alpha — Streamlit Dashboard
Run: streamlit run app_streamlit.py
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.data.universe_builder import build_sample_universe
from src.pipeline.daily_alpha_pipeline import run_pipeline

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WhaleWatch Alpha",
    page_icon="🐋",
    layout="wide",
)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🐋 WhaleWatch Alpha")
st.caption("NSE Multi-Factor Daily Stock Ranking Engine")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    top_n = st.slider("Top N Stocks", min_value=5, max_value=20, value=10, step=1)
    universe_size = st.slider("Universe Size (sample)", min_value=20, max_value=200, value=60, step=10)
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
    st.session_state.results = None

# ── Run pipeline ──────────────────────────────────────────────────────────────
if run_btn or st.session_state.results is None:
    with st.spinner("Running 7-factor alpha pipeline..."):
        universe_df = build_sample_universe(n=universe_size)
        results = run_pipeline(universe_df, top_n=top_n)
        st.session_state.results = results
    st.success(f"✅ Pipeline complete — Top {top_n} stocks ranked")

df = st.session_state.results

# ── KPI row ───────────────────────────────────────────────────────────────────
st.divider()
col1, col2, col3, col4 = st.columns(4)
col1.metric("Top Stock",   df["symbol"].iloc[0])
col2.metric("Best Score",  f"{df['final_score'].iloc[0]:.4f}")
col3.metric("Avg Score",   f"{df['final_score'].mean():.4f}")
col4.metric("Stocks Ranked", len(df))

st.divider()

# ── Main table ────────────────────────────────────────────────────────────────
st.subheader("📋 Top Alpha Stocks")

score_cols = ["final_score","technical","valuation","moat","quant","macro","risk","whale"]
display_df = df.copy()
for c in score_cols:
    if c in display_df.columns:
        display_df[c] = display_df[c].apply(lambda x: round(float(x), 4))

# Simple clean table — no matplotlib dependency
st.dataframe(display_df, use_container_width=True, height=420)

# ── Download button ───────────────────────────────────────────────────────────
csv_data = display_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Download CSV",
    data=csv_data,
    file_name="alpha_top10.csv",
    mime="text/csv",
)

st.divider()

# ── Charts ────────────────────────────────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🎯 Final Alpha Score")
    fig_bar = px.bar(
        df.sort_values("final_score"),
        x="final_score",
        y="symbol",
        orientation="h",
        color="final_score",
        color_continuous_scale="Teal",
        labels={"final_score": "Alpha Score", "symbol": "Stock"},
    )
    fig_bar.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        height=420,
        margin=dict(l=10, r=10, t=10, b=10),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("📡 Factor Breakdown — Top Stock")
    top_stock  = df.iloc[0]
    factor_cols = [c for c in ["technical","valuation","moat","quant","macro","whale"] if c in df.columns]
    factor_vals = [float(top_stock[c]) for c in factor_cols]

    fig_radar = go.Figure(go.Scatterpolar(
        r=factor_vals + [factor_vals[0]],
        theta=factor_cols + [factor_cols[0]],
        fill="toself",
        fillcolor="rgba(0,180,180,0.2)",
        line=dict(color="teal", width=2),
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=False,
        height=420,
        margin=dict(l=40, r=40, t=40, b=40),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

# ── Heatmap ───────────────────────────────────────────────────────────────────
st.divider()
st.subheader("🔥 Factor Heatmap — All Stocks")
heat_cols = [c for c in ["technical","valuation","moat","quant","macro","whale"] if c in df.columns]
heat_df   = df[["symbol"] + heat_cols].set_index("symbol").astype(float)

fig_heat = px.imshow(
    heat_df,
    color_continuous_scale="RdYlGn",
    aspect="auto",
    labels=dict(x="Factor", y="Stock", color="Score"),
    zmin=0, zmax=1,
)
fig_heat.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10))
st.plotly_chart(fig_heat, use_container_width=True)

st.caption("WhaleWatch Alpha — Sample data. Replace universe_builder.py with real NSE data.")
