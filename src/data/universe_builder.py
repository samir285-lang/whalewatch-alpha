"""
universe_builder.py
-------------------
Temporary sample universe with synthetic OHLCV + fundamental data.
Replace build_sample_universe() with your real NSE data loader later.
"""
import numpy as np
import pandas as pd


def _make_ohlcv(n: int = 260, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0005, 0.015, n)
    close = 100 * np.cumprod(1 + rets)
    high = close * (1 + np.abs(rng.normal(0, 0.006, n)))
    low = close * (1 - np.abs(rng.normal(0, 0.006, n)))
    volume = rng.integers(1_000_000, 6_000_000, n).astype(float)
    return pd.DataFrame({"close": close, "high": high, "low": low, "volume": volume})


def build_sample_universe(n: int = 60) -> pd.DataFrame:
    """Returns DataFrame of n stocks with all required columns."""
    sectors = [
        "capital_goods", "defence", "power", "infra",
        "banking", "nbfc", "real_estate", "auto",
        "it", "pharma", "fmcg", "metals",
    ]
    rng = np.random.default_rng(42)
    rows = []

    for i in range(n):
        rows.append({
            "symbol":       f"STK{i:03d}",
            "sector":       sectors[i % len(sectors)],
            "price_df":     _make_ohlcv(seed=i),
            "pe":           float(rng.uniform(8, 40)),
            "sector_pe":    float(rng.uniform(12, 30)),
            "pb":           float(rng.uniform(0.8, 6)),
            "ev_ebitda":    float(rng.uniform(5, 25)),
            "roe":          float(rng.uniform(5, 30)),
            "margin":       float(rng.uniform(3, 28)),
            "debt_equity":  float(rng.uniform(0.0, 2.0)),
            "revenue_cagr": float(rng.uniform(-5, 22)),
            "whale":        float(rng.uniform(0, 1)),
            "turnover_cr":  float(rng.uniform(2, 200)),
        })

    return pd.DataFrame(rows)
