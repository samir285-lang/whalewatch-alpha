"""
Macro Regime Engine  |  Weight: 10%
Sector scores calibrated for India capex + rate-cut cycle.
Update _SECTOR_SCORES quarterly.
"""
from typing import Optional

_SECTOR_SCORES = {
    "capital_goods": 1.00, "defence": 1.00,
    "power": 0.90,         "infra": 0.90,   "railways": 0.85,
    "banking": 0.75,       "nbfc": 0.70,
    "real_estate": 0.65,   "housing_finance": 0.65,
    "consumer_discretionary": 0.60, "auto": 0.55,
    "fmcg": 0.30,          "pharma": 0.35,  "healthcare": 0.35,
    "it": 0.25,
    "metals": 0.20,        "chemicals": 0.20, "textile": 0.10,
}


def macro_score(sector: Optional[str]) -> float:
    if not sector:
        return 0.30
    return _SECTOR_SCORES.get(sector.lower().strip(), 0.30)
