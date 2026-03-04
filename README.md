# WhaleWatch Alpha — Daily Multi-Factor Stock Ranking

Scores NSE stocks across 7 institutional factors and ranks Top 10 daily.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest -q
python -m src.app
```

## Factor Weights

| Factor           | Weight | Engine                  |
|------------------|--------|-------------------------|
| Technical Trend  | 25%    | citadel_technical.py    |
| Valuation        | 20%    | morgan_valuation.py     |
| Moat / Quality   | 15%    | bain_moat.py            |
| Quant Pattern    | 15%    | renaissance_quant.py    |
| Macro Regime     | 10%    | macro_engine.py         |
| Risk (inverted)  | 10%    | bridgewater_risk.py     |
| Whale Activity   |  5%    | (pre-computed input)    |

## Output

Prints Top-10 table in terminal and saves CSV to `/output/alpha_top10_YYYY-MM-DD.csv`.

## Replace Sample Data

Edit `src/data/universe_builder.py` and swap `build_sample_universe()`
with your real NSE data loader (yfinance, jugaad-data, etc.).
