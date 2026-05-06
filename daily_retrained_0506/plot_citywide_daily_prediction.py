from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def main() -> None:
    p = argparse.ArgumentParser(description="Plot Detroit citywide daily True vs Pred from panel_pred_test_2025_by_date.csv")
    p.add_argument(
        "--by-date-csv",
        default=r"daily_retrained_0506\out\out_date_0701_1030\panel_pred_test_2025_by_date.csv",
        help="Prediction by-date CSV (one row per grid_id per date).",
    )
    p.add_argument(
        "--out-png",
        default=r"daily_retrained_0506\out\out_date_0701_1030\citywide_daily_true_vs_pred.png",
        help="Output PNG path.",
    )
    p.add_argument("--date-start", default=None, help="Optional inclusive start date (YYYY-MM-DD)")
    p.add_argument("--date-end", default=None, help="Optional inclusive end date (YYYY-MM-DD)")
    p.add_argument("--title", default="Daily city-wide crowd flow (Detroit)", help="Plot title")
    args = p.parse_args()

    by_path = Path(args.by_date_csv)
    if not by_path.exists():
        raise SystemExit(f"Missing --by-date-csv: {by_path}")

    df = pd.read_csv(by_path, parse_dates=["date"])
    df["date"] = pd.to_datetime(df["date"]).dt.normalize()

    if args.date_start:
        df = df[df["date"] >= pd.Timestamp(args.date_start).normalize()]
    if args.date_end:
        df = df[df["date"] <= pd.Timestamp(args.date_end).normalize()]
    if len(df) == 0:
        raise SystemExit("No rows after date filtering.")

    need = {"y_true", "y_pred_mean"}
    miss = need - set(df.columns)
    if miss:
        raise SystemExit(f"Missing columns in by-date CSV: {sorted(miss)}")

    s = (
        df.groupby("date", as_index=False)
        .agg(true=("y_true", "sum"), pred=("y_pred_mean", "sum"))
        .sort_values("date")
        .reset_index(drop=True)
    )

    out_png = Path(args.out_png)
    out_png.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(12, 4.5), dpi=150)
    plt.plot(s["date"], s["true"], label="True (sum over grids)", linewidth=2.0)
    plt.plot(s["date"], s["pred"], label="Pred (mean, sum over grids)", linewidth=2.0)
    plt.title(args.title)
    plt.xlabel("Date")
    plt.ylabel("Visits (sum over Top-100 grids)")
    plt.grid(True, alpha=0.25)
    plt.legend(loc="best")
    plt.tight_layout()
    plt.savefig(out_png, bbox_inches="tight")
    print(f"Wrote: {out_png}")


if __name__ == "__main__":
    main()

