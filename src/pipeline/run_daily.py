"""
src/pipeline/run_daily.py
--------------------------
Entry point for GitHub Actions.
Runs pipeline for all 4 universes and saves CSVs to output/.
Triggered every weekday at 9 PM IST via .github/workflows/daily_pipeline.yml
"""
import logging
import sys
from pathlib import Path
from datetime import date

# Allow src imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.data.universe_builder import build_real_universe, UNIVERSE_MAP
from src.pipeline.daily_alpha_pipeline import run_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger(__name__)

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

TOP_N = 15   # save top 15 so dashboard can show 5/10/15 flexibly

def run_all():
    today = date.today().isoformat()
    summary = []

    for universe_name in UNIVERSE_MAP.keys():
        log.info(f"=== Starting: {universe_name} ===")

        try:
            universe_df = build_real_universe(universe=universe_name)

            if universe_df.empty:
                log.warning(f"{universe_name}: no data fetched, skipping")
                continue

            top = run_pipeline(universe_df, top_n=TOP_N)

            # Save as CSV
            slug = universe_name.lower().replace(" ", "_").replace("&", "and")
            csv_path = OUTPUT_DIR / f"{slug}_top{TOP_N}.csv"
            top.drop(columns=["price_df"], errors="ignore").to_csv(csv_path, index=False)

            # Also save a dated snapshot
            dated_path = OUTPUT_DIR / f"{slug}_top{TOP_N}_{today}.csv"
            top.drop(columns=["price_df"], errors="ignore").to_csv(dated_path, index=False)

            log.info(f"{universe_name}: saved {csv_path}")
            summary.append(f"  ✅ {universe_name}: {len(universe_df)} stocks scanned, top {TOP_N} saved")

        except Exception as e:
            log.error(f"{universe_name} failed: {e}")
            summary.append(f"  ❌ {universe_name}: FAILED — {e}")

    # Write last run metadata
    meta_path = OUTPUT_DIR / "last_run.txt"
    meta_path.write_text(
        f"Last run: {today}\n" +
        "\n".join(summary) + "\n"
    )
    log.info("=== Pipeline complete ===")
    for line in summary:
        log.info(line)


if __name__ == "__main__":
    run_all()
