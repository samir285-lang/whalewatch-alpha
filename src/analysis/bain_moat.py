"""
Bain Capital-style Moat Engine  |  Weight: 15%
Signals: ROE, Operating Margin, D/E, Revenue CAGR
"""
import numpy as np


def moat_score(roe: float, margin: float,
               debt_equity: float = None, revenue_cagr: float = None) -> float:
    s = 0.0
    if   roe > 25: s += 0.70
    elif roe > 20: s += 0.55
    elif roe > 15: s += 0.35
    elif roe > 10: s += 0.15

    if   margin > 25: s += 0.50
    elif margin > 15: s += 0.35
    elif margin >  8: s += 0.15

    if debt_equity is not None:
        s += 0.10 if debt_equity < 0.30 else (0.05 if debt_equity < 0.80 else 0.0)

    if revenue_cagr is not None:
        s += 0.10 if revenue_cagr > 15 else (0.05 if revenue_cagr > 8 else 0.0)

    return round(float(np.clip(s, 0.0, 1.4)), 4)
