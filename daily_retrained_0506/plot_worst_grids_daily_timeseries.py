from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def _plot_one(df_g: pd.DataFrame, grid_id: str, out_png: Path, title: str) -> None:
    df_g = df_g.sort_values("date").copy()
    plt.figure(figsize=(12, 4.5), dpi=150)
    plt.plot(df_g["date"], df_g["y_true"], label="True", linewidth=2.0)
    plt.plot(df_g["date"], df_g["y_pred_mean"], label="Pred (mean)", linewidth=2.0)
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Visits")
    plt.grid(True, alpha=0.25)
    plt.legend(loc="best")
    plt.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_png, bbox_inches="tight")
    plt.close()


def main() -> None:
    p = argparse.ArgumentParser(description="Plot daily time series for worst grids (True vs Pred).")
    p.add_argument(
        "--by-date-csv",
        default=r"daily_retrained_0506\out\out_date_0701_1030\panel_pred_test_2025_by_date.csv",
        help="Prediction by-date CSV (one row per grid per date).",
    )
    p.add_argument(
        "--metrics-csv",
        default=r"daily_retrained_0506\out\out_date_0701_1030\eval\worst3_metrics.csv",
        help="Worst-3 metrics CSV (grid_id column).",
    )
    p.add_argument(
        "--out-dir",
        default=r"daily_retrained_0506\out\out_date_0701_1030\worst3_plots",
        help="Output directory for PNGs.",
    )
    p.add_argument("--date-start", default=None)
    p.add_argument("--date-end", default=None)
    args = p.parse_args()

    by_path = Path(args.by_date_csv)
    if not by_path.exists():
        raise SystemExit(f"Missing --by-date-csv: {by_path}")
    m_path = Path(args.metrics_csv)
    if not m_path.exists():
        raise SystemExit(f"Missing --metrics-csv: {m_path}")

    m = pd.read_csv(m_path)
    if "grid_id" not in m.columns:
        raise SystemExit("metrics csv must contain grid_id column")
    worst_ids = m["grid_id"].astype(str).tolist()
    if not worst_ids:
        raise SystemExit("No grid_id found in metrics csv")

    df = pd.read_csv(by_path, parse_dates=["date"])
    df["grid_id"] = df["grid_id"].astype(str)
    df["date"] = pd.to_datetime(df["date"]).dt.normalize()

    if args.date_start:
        df = df[df["date"] >= pd.Timestamp(args.date_start).normalize()]
    if args.date_end:
        df = df[df["date"] <= pd.Timestamp(args.date_end).normalize()]

    need = {"grid_id", "date", "y_true", "y_pred_mean"}
    miss = need - set(df.columns)
    if miss:
        raise SystemExit(f"Missing columns in by-date csv: {sorted(miss)}")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for gid in worst_ids:
        dg = df[df["grid_id"] == gid].copy()
        if len(dg) == 0:
            continue
        out_png = out_dir / f"grid_{gid}_true_vs_pred.png"
        title = f"Daily grid true vs pred ({gid})"
        _plot_one(dg, gid, out_png, title)
        print(f"Wrote: {out_png}")


if __name__ == "__main__":
    main()

