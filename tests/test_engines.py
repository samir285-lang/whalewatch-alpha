import pandas as pd
import numpy as np

from src.analysis.citadel_technical  import technical_score
from src.analysis.morgan_valuation   import valuation_score
from src.analysis.bain_moat          import moat_score
from src.analysis.renaissance_quant  import quant_score
from src.analysis.bridgewater_risk   import risk_score
from src.analysis.macro_engine       import macro_score
from src.ranking.master_ranking      import compute_final_score, rank_universe


def _df(n=260, seed=1):
    rng = np.random.default_rng(seed)
    c = 100 * np.cumprod(1 + rng.normal(0.0005, 0.015, n))
    h = c * (1 + np.abs(rng.normal(0, 0.006, n)))
    l = c * (1 - np.abs(rng.normal(0, 0.006, n)))
    v = rng.integers(1_000_000, 6_000_000, n).astype(float)
    return pd.DataFrame({"close": c, "high": h, "low": l, "volume": v})


def test_technical():   assert isinstance(technical_score(_df()), float)
def test_valuation():   assert valuation_score(10, 20) == 1.0
def test_moat():        assert moat_score(22, 18) > 0
def test_quant():       assert isinstance(quant_score(_df()), float)
def test_risk():        assert 0.10 <= risk_score(_df()) <= 1.00
def test_macro():       assert macro_score("defence") == 1.0
def test_macro_null():  assert macro_score(None) == 0.30

def test_rank():
    df = pd.DataFrame([
        {"symbol":"GOOD","technical":1,"valuation":1,"moat":1,"quant":1,"macro":1,"risk":0.1,"whale":1},
        {"symbol":"BAD", "technical":0,"valuation":0,"moat":0,"quant":0,"macro":0,"risk":0.9,"whale":0},
    ])
    out = rank_universe(df, top_n=1)
    assert out.iloc[0]["symbol"] == "GOOD"
