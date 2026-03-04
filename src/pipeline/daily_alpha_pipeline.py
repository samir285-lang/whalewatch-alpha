"""
Daily Alpha Pipeline
Runs all 7 factor engines, merges scores, returns ranked Top-N DataFrame.
"""
import pandas as pd
import logging

from src.analysis.citadel_technical  import technical_score
from src.analysis.morgan_valuation   import valuation_score
from src.analysis.bain_moat          import moat_score
from src.analysis.renaissance_quant  import quant_score
from src.analysis.bridgewater_risk   import risk_score
from src.analysis.macro_engine       import macro_score
from src.ranking.master_ranking      import rank_universe

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


def _safe(fn, *args, default=0.0, label=""):
    try:    return fn(*args)
    except Exception as e:
        log.warning(f"[{label}] {fn.__name__} failed: {e}")
        return default


def run_pipeline(universe_df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    df = universe_df.copy()
    log.info(f"Pipeline started — {len(df)} stocks")

    df["technical"] = df.apply(lambda r: _safe(technical_score,  r["price_df"],
                                label=r.get("symbol","")), axis=1)
    df["valuation"] = df.apply(lambda r: _safe(valuation_score,  r["pe"], r["sector_pe"],
                                r.get("pb"), r.get("ev_ebitda"), label=r.get("symbol","")), axis=1)
    df["moat"]      = df.apply(lambda r: _safe(moat_score,        r["roe"], r["margin"],
                                r.get("debt_equity"), r.get("revenue_cagr"), label=r.get("symbol","")), axis=1)
    df["quant"]     = df.apply(lambda r: _safe(quant_score,       r["price_df"],
                                label=r.get("symbol","")), axis=1)
    df["risk"]      = df.apply(lambda r: _safe(risk_score,        r["price_df"],
                                r.get("index_df"), r.get("turnover_cr"), label=r.get("symbol","")), axis=1)
    df["macro"]     = df.apply(lambda r: _safe(macro_score,       r.get("sector",""),
                                label=r.get("symbol","")), axis=1)

    if "whale" not in df.columns:
        df["whale"] = 0.0

    top = rank_universe(df, top_n=top_n, normalize=True)
    cols = ["symbol","final_score","whale","technical","valuation","moat","quant","macro","risk"]
    return top[[c for c in cols if c in top.columns]]
