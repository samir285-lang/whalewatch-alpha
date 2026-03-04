"""
Morgan Stanley-style Valuation Engine  |  Weight: 20%
Signals: PE vs sector, PB, EV/EBITDA
"""
import numpy as np


def valuation_score(pe: float, sector_pe: float,
                    pb: float = None, ev_ebitda: float = None) -> float:
    if not (pe and pe > 0 and sector_pe and sector_pe > 0):
        return 0.0
    ratio = pe / sector_pe
    if   ratio < 0.70: pe_s =  1.00
    elif ratio < 0.85: pe_s =  0.70
    elif ratio < 1.00: pe_s =  0.40
    elif ratio < 1.20: pe_s =  0.00
    else:              pe_s = -0.50

    pb_b = 0.25 if (pb and 0 < pb < 1.0) else (0.10 if (pb and pb < 2.5) else 0.0)
    ev_b = 0.25 if (ev_ebitda and ev_ebitda < 8) else (0.10 if (ev_ebitda and ev_ebitda < 15) else 0.0)
    return round(float(np.clip(pe_s + pb_b + ev_b, -1.0, 1.5)), 4)
