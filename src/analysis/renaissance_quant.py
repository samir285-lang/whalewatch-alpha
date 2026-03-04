"""
Renaissance-style Quant Pattern Engine  |  Weight: 15%
Signals: Volume spike, 10-day momentum, 52W breakout, Z-score mean reversion
"""
import pandas as pd
import numpy as np


def quant_score(df: pd.DataFrame) -> float:
    if len(df) < 20:
        return 0.0
    close, volume = df["close"], df["volume"]
    s = 0.0

    vol_avg = volume.rolling(20).mean().iloc[-1]
    if vol_avg > 0:
        r = volume.iloc[-1] / vol_avg
        s += 0.40 if r > 1.5 else (0.20 if r > 1.2 else 0.0)

    m10 = float(close.pct_change(10).iloc[-1])
    s += 0.50 if m10 > 0.08 else (0.30 if m10 > 0.04 else (-0.20 if m10 < -0.08 else 0.0))

    if len(df) >= 252:
        if close.iloc[-1] >= close.iloc[-252:].max() * 0.98:
            s += 0.40

    std20 = close.rolling(20).std().iloc[-1]
    if std20 > 0:
        z = (close.iloc[-1] - close.rolling(20).mean().iloc[-1]) / std20
        if z > 2.5:
            s -= 0.20

    return round(float(np.clip(s, 0.0, 1.5)), 4)
