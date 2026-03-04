import pandas as pd
from datetime import date
from pathlib import Path


def format_console_table(df: pd.DataFrame) -> str:
    cols = ["symbol","final_score","whale","technical","valuation","moat","quant","macro","risk"]
    cols = [c for c in cols if c in df.columns]
    header = " | ".join(f"{c:>13}" for c in cols)
    sep    = "-" * len(header)
    rows   = [header, sep]
    for _, r in df.iterrows():
        rows.append(" | ".join(f"{str(round(r[c],4)):>13}" for c in cols))
    return "\n".join(rows)


def export_csv(df: pd.DataFrame, output_dir: str = "output") -> str:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    path = f"{output_dir}/alpha_top10_{date.today().isoformat()}.csv"
    df.to_csv(path, index=False)
    return path
