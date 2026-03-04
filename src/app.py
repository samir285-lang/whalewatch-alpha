from src.config import CONFIG
from src.data.universe_builder import build_sample_universe
from src.pipeline.daily_alpha_pipeline import run_pipeline
from src.pipeline.output_formatter import format_console_table, export_csv

def main():
    universe_df = build_sample_universe(n=60)
    top = run_pipeline(universe_df, top_n=CONFIG.top_n)
    print("\n=== Top Alpha Stocks (Today) ===\n")
    print(format_console_table(top))
    out = export_csv(top, output_dir=CONFIG.output_dir)
    print(f"\nSaved: {out}")

if __name__ == "__main__":
    main()
