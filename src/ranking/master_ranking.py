"""
Master Alpha Ranking Engine
Normalises all factor scores to [0,1] before weighting to remove scale bias.
"""
import pandas as pd

WEIGHTS = {
    "technical": 0.25,
    "valuation": 0.20,
    "moat":      0.15,
    "quant":     0.15,
    "macro":     0.10,
    "risk":      0.10,   # applied as (1 - risk)
    "whale":     0.05,
}


def _normalize(s: pd.Series) -> pd.Series:
    mn, mx = s.min(), s.max()
    if mx == mn:
        return pd.Series([0.5] * len(s), index=s.index)
    return (s - mn) / (mx - mn)


def compute_final_score(row: pd.Series) -> float:
    return round(
        WEIGHTS["technical"] * float(row.get("technical", 0)) +
        WEIGHTS["valuation"] * float(row.get("valuation",  0)) +
        WEIGHTS["moat"]      * float(row.get("moat",       0)) +
        WEIGHTS["quant"]     * float(row.get("quant",      0)) +
        WEIGHTS["macro"]     * float(row.get("macro",      0)) +
        WEIGHTS["risk"]      * (1.0 - float(row.get("risk", 0.5))) +
        WEIGHTS["whale"]     * float(row.get("whale",      0)),
        4
    )


def rank_universe(df: pd.DataFrame, top_n: int = 10,
                  normalize: bool = True) -> pd.DataFrame:
    result = df.copy()
    if normalize:
        for c in ["technical", "valuation", "moat", "quant", "macro", "whale", "risk"]:
            if c in result.columns:
                result[c] = _normalize(result[c])
    result["final_score"] = result.apply(compute_final_score, axis=1)
    return result.sort_values("final_score", ascending=False).head(top_n).reset_index(drop=True)
