"""
Bridgewater-style Risk Engine  |  Weight: 10% (used as 1 - risk_score)
Signals: Annualised vol, Max drawdown, Beta vs Nifty, Liquidity
"""
import pandas as pd
import numpy as np
from typing import Optional


def _max_drawdown(close: pd.Series, window: int = 60) -> float:
    s = close.iloc[-window:]
    return float(((s - s.cummax()) / s.cummax()).min())


def _beta(sr: pd.Series, ir: pd.Series) -> float:
    if len(sr) < 30 or len(ir) < 30:
        return 1.0
    cov = np.cov(sr.values[-60:], ir.values[-60:])
    return float(cov[0, 1] / cov[1, 1]) if cov[1, 1] != 0 else 1.0


def risk_score(df: pd.DataFrame,
               index_df: Optional[pd.DataFrame] = None,
               avg_daily_turnover_cr: Optional[float] = None) -> float:
    """Returns float [0.1, 1.0]. Lower = safer. Used as (1 - risk_score) in alpha."""
    if len(df) < 30:
        return 0.50

    ret = df["close"].pct_change().dropna()
    vol = float(ret.iloc[-30:].std() * np.sqrt(252))

    if   vol < 0.20: vs = 0.15
    elif vol < 0.35: vs = 0.40
    elif vol < 0.55: vs = 0.65
    else:            vs = 0.90

    mdd = _max_drawdown(df["close"])
    ms  = 0.10 if mdd > -0.10 else (0.35 if mdd > -0.20 else 0.70)

    bs = 0.0
    if index_df is not None:
        b  = _beta(ret, index_df["close"].pct_change().dropna())
        bs = min(abs(b) * 0.10, 0.20)

    lp = 0.0
    if avg_daily_turnover_cr is not None:
        lp = 0.20 if avg_daily_turnover_cr < 5 else (0.10 if avg_daily_turnover_cr < 20 else 0.0)

    return round(float(np.clip(vs * 0.50 + ms * 0.35 + bs + lp, 0.10, 1.00)), 4)
