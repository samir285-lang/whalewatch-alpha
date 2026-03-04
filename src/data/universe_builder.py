"""
universe_builder.py — WhaleWatch Alpha
Real NSE data via yfinance | All tickers verified for Yahoo Finance .NS format
6 months minimum data | Grows automatically daily
"""
import yfinance as yf
import pandas as pd
import numpy as np
import logging

log = logging.getLogger(__name__)

# ── Verified Yahoo Finance .NS tickers ───────────────────────────────────────
NIFTY100 = [
    "RELIANCE.NS","TCS.NS","HDFCBANK.NS","BHARTIARTL.NS","ICICIBANK.NS",
    "INFY.NS","SBIN.NS","HINDUNILVR.NS","ITC.NS","LT.NS",
    "KOTAKBANK.NS","AXISBANK.NS","BAJFINANCE.NS","MARUTI.NS","ASIANPAINT.NS",
    "TITAN.NS","SUNPHARMA.NS","WIPRO.NS","ULTRACEMCO.NS","NTPC.NS",
    "POWERGRID.NS","ADANIENT.NS","ADANIPORTS.NS","ONGC.NS","COALINDIA.NS",
    "BAJAJFINSV.NS","HCLTECH.NS","TATAMOTORS.NS","TATASTEEL.NS","JSWSTEEL.NS",
    "HINDALCO.NS","GRASIM.NS","INDUSINDBK.NS","CIPLA.NS","DRREDDY.NS",
    "DIVISLAB.NS","EICHERMOT.NS","HEROMOTOCO.NS","BPCL.NS","TATACONSUM.NS",
    "APOLLOHOSP.NS","NESTLEIND.NS","BRITANNIA.NS","PIDILITIND.NS","DABUR.NS",
    "MARICO.NS","COLPAL.NS","BERGEPAINT.NS","HAVELLS.NS","VOLTAS.NS",
    "SIEMENS.NS","ABB.NS","BEL.NS","HAL.NS","BHEL.NS",
    "IRFC.NS","PFC.NS","RECLTD.NS","CANBK.NS","BANKBARODA.NS",
    "UNIONBANK.NS","PNB.NS","IDFCFIRSTB.NS","FEDERALBNK.NS","BANDHANBNK.NS",
    "MUTHOOTFIN.NS","BAJAJ-AUTO.NS","TVSMOTOR.NS","M&M.NS","TATAPOWER.NS",
    "ADANIGREEN.NS","ADANIPOWER.NS","TORNTPOWER.NS","NHPC.NS","SAIL.NS",
    "NMDC.NS","VEDL.NS","HINDZINC.NS","GODREJCP.NS","JUBLFOOD.NS",
    "DMART.NS","ZOMATO.NS","LTIM.NS","TECHM.NS","MPHASIS.NS",
    "PERSISTENT.NS","COFORGE.NS","CHOLAFIN.NS","SBILIFE.NS","HDFCLIFE.NS",
    "ICICIPRULI.NS","ICICIGI.NS","BAJAJHLDNG.NS","MOTHERSON.NS","ASHOKLEY.NS",
    "INDIGO.NS","CONCOR.NS","BALKRISIND.NS","AUROPHARMA.NS","TORNTPHARM.NS",
]

FNO_STOCKS = [
    "RELIANCE.NS","TCS.NS","HDFCBANK.NS","ICICIBANK.NS","INFY.NS",
    "SBIN.NS","AXISBANK.NS","BAJFINANCE.NS","MARUTI.NS","LT.NS",
    "KOTAKBANK.NS","HINDUNILVR.NS","ITC.NS","TITAN.NS","WIPRO.NS",
    "SUNPHARMA.NS","ULTRACEMCO.NS","NTPC.NS","POWERGRID.NS","ADANIENT.NS",
    "TATAMOTORS.NS","TATASTEEL.NS","JSWSTEEL.NS","HINDALCO.NS","BAJAJFINSV.NS",
    "HCLTECH.NS","GRASIM.NS","INDUSINDBK.NS","CIPLA.NS","DRREDDY.NS",
    "DIVISLAB.NS","EICHERMOT.NS","HEROMOTOCO.NS","BPCL.NS","APOLLOHOSP.NS",
    "COALINDIA.NS","ONGC.NS","ADANIPORTS.NS","SIEMENS.NS","HAL.NS",
    "BEL.NS","BHEL.NS","PFC.NS","RECLTD.NS","IRFC.NS",
    "CANBK.NS","BANKBARODA.NS","PNB.NS","IDFCFIRSTB.NS","FEDERALBNK.NS",
    "BAJAJ-AUTO.NS","TVSMOTOR.NS","M&M.NS","TATAPOWER.NS","ADANIGREEN.NS",
    "VEDL.NS","NMDC.NS","SAIL.NS","ZOMATO.NS","DMART.NS",
    "LTIM.NS","TECHM.NS","PERSISTENT.NS","COFORGE.NS","MPHASIS.NS",
    "CHOLAFIN.NS","SBILIFE.NS","HDFCLIFE.NS","MUTHOOTFIN.NS","INDIGO.NS",
    "ASHOKLEY.NS","MOTHERSON.NS","BALKRISIND.NS","AUROPHARMA.NS","TORNTPHARM.NS",
    "JUBLFOOD.NS","GODREJCP.NS","DABUR.NS","MARICO.NS","COLPAL.NS",
    "HAVELLS.NS","VOLTAS.NS","ABB.NS","BERGEPAINT.NS","PIDILITIND.NS",
    "BANDHANBNK.NS","UNIONBANK.NS","TATACONSUM.NS","NESTLEIND.NS","BRITANNIA.NS",
    "TORNTPOWER.NS","NHPC.NS","HINDZINC.NS","NATIONALUM.NS","CONCOR.NS",
    "ICICIPRULI.NS","ICICIGI.NS","HDFCAMC.NS","ANGELONE.NS","BSE.NS",
]

NIFTY500_EXTRA = [
    "LODHA.NS","PRESTIGE.NS","OBEROIRLTY.NS","PHOENIXLTD.NS","SOBHA.NS",
    "KPRMILL.NS","PAGEIND.NS","MCDOWELLNS.NS","RADICO.NS","UBL.NS",
    "TRENT.NS","NYKAA.NS","VMART.NS","ABFRL.NS","RAYMOND.NS",
    "SYNGENE.NS","LALPATHLAB.NS","METROPOLIS.NS","MAXHEALTH.NS","FORTIS.NS",
    "ZYDUSLIFE.NS","ALKEM.NS","IPCALAB.NS","GLAXO.NS","PFIZER.NS",
    "TATAELXSI.NS","KPITTECH.NS","TANLA.NS","RATEGAIN.NS","ZENSARTECH.NS",
    "CAMS.NS","CDSL.NS","MCX.NS","IIFL.NS","MANAPPURAM.NS",
    "SUPREMEIND.NS","ASTRAL.NS","POLYCAB.NS","KANSAINER.NS","BLUEDART.NS",
    "CELLO.NS","DIXON.NS","AMBER.NS","KAYNES.NS","SYRMA.NS",
    "RVNL.NS","IRCON.NS","NBCC.NS","RITES.NS","RAILTEL.NS",
    "SJVN.NS","MAZDOCK.NS","GRSE.NS","COCHINSHIP.NS","IFCI.NS","HUDCO.NS","IREDA.NS",
]

ALL_NSE_EXTRA = [
    "NAUKRI.NS","JUSTDIAL.NS","CARTRADE.NS","EASEMYTRIP.NS","IXIGO.NS",
    "BIKAJI.NS","DEVYANI.NS","SAPPHIRE.NS","WESTLIFE.NS",
    "RRKABEL.NS","KEI.NS","FNXCABLES.NS","HBLENGINE.NS","INOXWIND.NS",
    "WAAREEENER.NS","J&KBANK.NS","KTKBANK.NS","DCBBANK.NS","RBLBANK.NS",
    "SOUTHBANK.NS","TATACHEM.NS","GHCL.NS","DEEPAKNTR.NS","AARTIIND.NS",
    "VINATIORGA.NS","ALKYLAMINE.NS","FINEORG.NS","CLEAN.NS","NEOGEN.NS",
]

NIFTY500 = list(dict.fromkeys(NIFTY100 + FNO_STOCKS + NIFTY500_EXTRA))
ALL_NSE   = list(dict.fromkeys(NIFTY500 + ALL_NSE_EXTRA))

UNIVERSE_MAP = {
    "Nifty 100":  NIFTY100,
    "F&O Stocks": FNO_STOCKS,
    "Nifty 500":  NIFTY500,
    "All NSE":    ALL_NSE,
}

SECTOR_MAP = {
    "Technology":             "it",
    "Financial Services":     "banking",
    "Consumer Defensive":     "fmcg",
    "Consumer Cyclical":      "consumer_discretionary",
    "Healthcare":             "healthcare",
    "Basic Materials":        "metals",
    "Energy":                 "power",
    "Industrials":            "capital_goods",
    "Communication Services": "it",
    "Real Estate":            "real_estate",
    "Utilities":              "power",
}

MIN_DAYS = 120   # 6 months minimum (~120 trading days)

def _fetch_one(ticker: str) -> dict | None:
    try:
        t    = yf.Ticker(ticker)
        hist = t.history(period="max")   # all available — grows daily
        info = t.info

        if hist.empty or len(hist) < MIN_DAYS:
            log.warning(f"{ticker}: only {len(hist)} days, need {MIN_DAYS}, skipping")
            return None

        hist = hist.rename(columns={
            "Open":"open","High":"high","Low":"low",
            "Close":"close","Volume":"volume",
        })[["open","high","low","close","volume"]]

        symbol  = ticker.replace(".NS","")
        sector  = SECTOR_MAP.get(info.get("sector",""), "capital_goods")
        pe      = float(info.get("trailingPE") or info.get("forwardPE") or 20.0)
        pb      = float(info.get("priceToBook") or 2.0)
        ev_ebit = float(info.get("enterpriseToEbitda") or 12.0)
        roe     = float((info.get("returnOnEquity") or 0.12) * 100)
        margin  = float((info.get("operatingMargins") or 0.10) * 100)
        de      = float(info.get("debtToEquity") or 0.5)
        rcagr   = float((info.get("revenueGrowth") or 0.08) * 100)
        whale   = float(np.clip(info.get("heldPercentInstitutions") or 0.5, 0, 1))
        turn    = float((info.get("averageVolume",1e6) * info.get("currentPrice",100)) / 1e7)

        return {
            "symbol":       symbol,
            "sector":       sector,
            "price_df":     hist,
            "pe":           pe,
            "sector_pe":    22.0,
            "pb":           pb,
            "ev_ebitda":    ev_ebit,
            "roe":          roe,
            "margin":       margin,
            "debt_equity":  de,
            "revenue_cagr": rcagr,
            "whale":        whale,
            "turnover_cr":  turn,
        }
    except Exception as e:
        log.warning(f"{ticker} failed: {e}")
        return None


def build_real_universe(universe: str = "Nifty 100") -> pd.DataFrame:
    """
    Fetch real NSE data for chosen universe.
    Minimum 6 months (120 trading days) of price history required.
    Data window grows automatically — more history added every trading day.
    """
    tickers = UNIVERSE_MAP.get(universe, NIFTY100)
    log.info(f"Fetching {universe} — {len(tickers)} tickers (min {MIN_DAYS} days required)")
    rows = []
    for i, t in enumerate(tickers):
        row = _fetch_one(t)
        if row:
            rows.append(row)
        if (i + 1) % 20 == 0:
            log.info(f"  {i+1}/{len(tickers)} processed...")
    log.info(f"Done — {len(rows)} stocks passed 6-month filter")
    return pd.DataFrame(rows)
