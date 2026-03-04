"""
WhaleWatch Alpha — Streamlit Dashboard
Reads pre-computed CSVs from output/ (generated nightly by GitHub Actions).
Zero heavy computation on dashboard side.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import date

st.set_page_config(page_title="WhaleWatch Alpha", page_icon="🐋", layout="wide")

OUTPUT_DIR = Path(__file__).parent / "output"

UNIVERSE_FILES = {
    "🔵 Nifty 100":  "nifty_100_top15.csv",
    "🟢 F&O Stocks": "fando_stocks_top15.csv",
    "🟡 Nifty 500":  "nifty_500_top15.csv",
    "🔴 All NSE":    "all_nse_top15.csv",
}

FACTOR_COLS = ["technical","valuation","moat","quant","macro","risk","whale"]
SCORE_COLS  = ["final_score"] + FACTOR_COLS

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🐋 WhaleWatch Alpha")
st.caption(f"NSE Multi-Factor Daily Stock Ranking  •  {date.today().strftime('%d %b %Y')}")

# ── Last run info ─────────────────────────────────────────────────────────────
meta_file = OUTPUT_DIR / "last_run.txt"
if meta_file.exists():
    st.info(meta_file.read_text(), icon="🕙")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    universe_label = st.radio(
        "📊 Stock Universe",
        options=list(UNIVERSE_FILES.keys()),
        index=0,
    )
    top_n = st.slider("Top N to display", 5, 15, 10)
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
    st.divider()
    st.caption("⏰ Pipeline runs every weekday at 9 PM IST automatically via GitHub Actions.")

# ── Load data ─────────────────────────────────────────────────────────────────
csv_file = OUTPUT_DIR / UNIVERSE_FILES[universe_label]

if not csv_file.exists():
    st.warning(
        f"No data yet for **{universe_label}**.\n\n"
        "The pipeline runs every weekday at 9 PM IST. "
        "You can also trigger it manually:\n"
        "GitHub repo → Actions → Daily Alpha Pipeline → Run workflow."
    )
    st.stop()

df = pd.read_csv(csv_file).head(top_n)
for c in SCORE_COLS:
    if c in df.columns:
        df[c] = df[c].apply(lambda x: round(float(x), 4))

# ── KPI row ───────────────────────────────────────────────────────────────────
st.divider()
c1,c2,c3,c4 = st.columns(4)
c1.metric("🏆 Top Stock",      df["symbol"].iloc[0])
c2.metric("⭐ Best Score",     f"{df['final_score'].iloc[0]:.4f}")
c3.metric("📊 Avg Score",      f"{df['final_score'].mean():.4f}")
c4.metric("📋 Stocks Shown",   top_n)
st.divider()

# ── Main table ────────────────────────────────────────────────────────────────
st.subheader(f"📋 Top {top_n} Alpha Stocks — {universe_label}")
st.dataframe(df, use_container_width=True, height=420)
csv_data = df.to_csv(index=False).encode("utf-8")
st.download_button("📥 Download CSV", csv_data, "alpha_top10.csv", "text/csv")

st.divider()

# ── Bar chart + Radar ─────────────────────────────────────────────────────────
cl, cr = st.columns(2)

with cl:
    st.subheader("🎯 Final Alpha Score")
    fig_bar = px.bar(
        df.sort_values("final_score"),
        x="final_score", y="symbol", orientation="h",
        color="final_score", color_continuous_scale="Teal",
        labels={"final_score":"Alpha Score","symbol":"Stock"},
    )
    fig_bar.update_layout(
        showlegend=False, coloraxis_showscale=False,
        height=420, margin=dict(l=10,r=10,t=10,b=10),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with cr:
    st.subheader(f"📡 Factor Breakdown — {df['symbol'].iloc[0]}")
    top_row = df.iloc[0]
    fcols   = [c for c in FACTOR_COLS if c in df.columns and c != "risk"]
    fvals   = [float(top_row[c]) for c in fcols]
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

# ── Heatmap ───────────────────────────────────────────────────────────────────
st.divider()
st.subheader("🔥 Factor Heatmap — All Ranked Stocks")
hcols   = [c for c in FACTOR_COLS if c in df.columns and c != "risk"]
heat_df = df[["symbol"]+hcols].set_index("symbol").astype(float)
fig_heat = px.imshow(
    heat_df, color_continuous_scale="RdYlGn", aspect="auto",
    labels=dict(x="Factor",y="Stock",color="Score"), zmin=0, zmax=1,
)
fig_heat.update_layout(height=420, margin=dict(l=10,r=10,t=10,b=10))
st.plotly_chart(fig_heat, use_container_width=True)

st.caption("WhaleWatch Alpha | Scores computed nightly | Data: Yahoo Finance NSE")
