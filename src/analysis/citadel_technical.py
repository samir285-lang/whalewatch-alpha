"""
Citadel-style Technical Trend Engine  |  Weight: 25%
Signals: MA50/MA200 cross, 20-day momentum, RSI filter, ATR filter
"""
import pandas as pd
import numpy as np


def _rsi(series: pd.Series, period: int = 14) -> float:
    delta = series.diff().dropna()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return float((100 - (100 / (1 + rs))).iloc[-1])


def _atr_norm(df: pd.DataFrame, period: int = 14) -> float:
    tr = pd.concat([
        df["high"] - df["low"],
        (df["high"] - df["close"].shift()).abs(),
        (df["low"]  - df["close"].shift()).abs(),
    ], axis=1).max(axis=1)
    atr = tr.ewm(span=period, min_periods=period).mean().iloc[-1]
    return float(atr / df["close"].iloc[-1])


def technical_score(df: pd.DataFrame) -> float:
    """Requires columns: close, high, low, volume. Min 200 rows."""
    if len(df) < 200:
        return 0.0
    close  = df["close"]
    trend  = 1.0 if close.rolling(50).mean().iloc[-1] > close.rolling(200).mean().iloc[-1] else -1.0
    mom    = float(np.clip(close.pct_change(20).iloc[-1], -0.30, 0.30))
    rsi_v  = _rsi(close)
    rsi_a  = -0.20 if rsi_v > 75 else (0.20 if rsi_v < 30 else 0.0)
    try:    atr_a = 0.10 if _atr_norm(df) < 0.02 else 0.0
    except: atr_a = 0.0
    return round(trend + mom + rsi_a + atr_a, 4)
