"""
src/pipeline/run_daily.py
Daily pipeline entry point for GitHub Actions.
Runs all 4 universes, saves CSVs, writes last_run metadata.
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
import pytz

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.data.universe_builder import build_real_universe, UNIVERSE_MAP
from src.pipeline.daily_alpha_pipeline import run_pipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)
TOP_N = 15

IST = pytz.timezone("Asia/Kolkata")

def run_all():
    now_ist = datetime.now(IST).strftime("%d %b %Y, %I:%M %p IST")
    summary = [f"Last updated: {now_ist}", ""]

    for universe_name in UNIVERSE_MAP.keys():
        log.info(f"=== {universe_name} ===")
        try:
            universe_df = build_real_universe(universe=universe_name)
            if universe_df.empty:
                summary.append(f"❌ {universe_name}: no data")
                continue

            top = run_pipeline(universe_df, top_n=TOP_N)
            slug = universe_name.lower().replace(" ","_").replace("&","and")
            csv_path = OUTPUT_DIR / f"{slug}_top{TOP_N}.csv"
            top.drop(columns=["price_df"], errors="ignore").to_csv(csv_path, index=False)

            days = int(universe_df["price_df"].apply(len).mean())
            summary.append(
                f"✅ {universe_name}: {len(universe_df)} stocks | "
                f"~{days} trading days history | top {TOP_N} saved"
            )
        except Exception as e:
            log.error(f"{universe_name} failed: {e}")
            summary.append(f"❌ {universe_name}: FAILED — {e}")

    (OUTPUT_DIR / "last_run.txt").write_text("\n".join(summary) + "\n")
    log.info("=== All done ===")
    for line in summary:
        log.info(line)

if __name__ == "__main__":
    run_all()
