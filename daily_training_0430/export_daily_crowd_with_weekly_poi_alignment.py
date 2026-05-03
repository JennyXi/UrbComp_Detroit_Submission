"""
Merge daily crowd-flow predictions (this folder) with frozen weekly POI alignment
(`weekly_alignment/alignment_jul_sep_2025.csv` + same scarcity_q logic as weekly four-layer export).

Outputs (under daily_training_0430/):

1) Long table: each daily row + weekly alignment attributes (prefixed walign_).
2) Grid summary: Jul–Sep daily mean prediction + n_days + weekly alignment + scarcity_q.
3) Four CSV + four GPKG for QGIS (one POI super-category each), same geometry as other grid exports.

Crowd side for Jul–Sep uses YOUR daily model's y_pred_mean averaged over calendar days in window.
POI / r_alignment side comes from the weekly alignment table you already computed.

Run from repo root:

  python daily_training_0430/export_daily_crowd_with_weekly_poi_alignment.py
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import pandas as pd

POI_COUNT_COLS = [
    "poi_cnt_life",
    "poi_cnt_transport",
    "poi_cnt_economy",
    "poi_cnt_public_service",
]

COL2LABEL = {
    "poi_cnt_life": "life",
    "poi_cnt_transport": "transport",
    "poi_cnt_economy": "economy",
    "poi_cnt_public_service": "public_service",
}


def main() -> None:
    here = Path(__file__).resolve().parent
    repo_root = here.parent

    parser = argparse.ArgumentParser(
        description="Join daily predictions with weekly POI alignment; write CSV + four GPKG maps."
    )
    parser.add_argument(
        "--daily-pred-csv",
        type=str,
        default=str(here / "panel_pred_test_2025_by_date.csv"),
        help="Daily long predictions (grid_id, date, y_pred_mean, ...).",
    )
    parser.add_argument(
        "--weekly-alignment-csv",
        type=str,
        default=str(repo_root / "weekly_alignment" / "alignment_jul_sep_2025.csv"),
        help="Per-grid weekly alignment from compute_alignment.py.",
    )
    parser.add_argument(
        "--date-start",
        type=str,
        default="2025-07-01",
        help="Jul–Sep crowd window start (match weekly_alignment jul_sep).",
    )
    parser.add_argument(
        "--date-end",
        type=str,
        default="2025-09-30",
        help="Jul–Sep crowd window end.",
    )
    parser.add_argument(
        "--tag",
        type=str,
        default="jul_sep_2025",
        help="Stem for output filenames.",
    )
    parser.add_argument(
        "--grid-weekly-parquet",
        type=str,
        default="data/grid100_weekly_2024_2025.parquet",
        help="Geometry index for GPKG export.",
    )
    args = parser.parse_args()

    pred_path = Path(args.daily_pred_csv)
    if not pred_path.is_absolute():
        pred_path = (repo_root / pred_path).resolve()
    aln_path = Path(args.weekly_alignment_csv)
    if not aln_path.is_absolute():
        aln_path = (repo_root / aln_path).resolve()

    if not pred_path.exists():
        raise SystemExit(f"Missing daily predictions: {pred_path}")
    if not aln_path.exists():
        raise SystemExit(f"Missing weekly alignment: {aln_path}")

    export_gpkg = repo_root / "weekly_alignment" / "export_alignment_gpkg.py"
    if not export_gpkg.exists():
        export_gpkg = repo_root / "scripts" / "export_alignment_gpkg.py"
    if not export_gpkg.exists():
        raise SystemExit("Could not find export_alignment_gpkg.py")

    d0 = pd.Timestamp(args.date_start).normalize()
    d1 = pd.Timestamp(args.date_end).normalize()

    pred = pd.read_csv(pred_path, parse_dates=["date"])
    pred["grid_id"] = pred["grid_id"].astype(str)
    pred_win = pred[(pred["date"] >= d0) & (pred["date"] <= d1)].copy()
    if pred_win.empty:
        raise SystemExit(f"No daily rows in [{d0.date()}, {d1.date()}].")

    aln = pd.read_csv(aln_path)
    aln["grid_id"] = aln["grid_id"].astype(str)
    for c in POI_COUNT_COLS:
        if c not in aln.columns:
            raise SystemExit(f"Weekly alignment missing {c}")
        aln[c] = pd.to_numeric(aln[c], errors="coerce").fillna(0.0)

    # --- Long: daily rows + weekly alignment (prefixed) ---
    aln_pref = aln.rename(columns={c: f"walign_{c}" for c in aln.columns if c != "grid_id"})
    long = pred_win.merge(aln_pref, on="grid_id", how="left")
    long_out = here / f"panel_pred_by_date_walign_{args.tag}.csv"
    long.to_csv(long_out, index=False)

    # --- Per-grid: daily aggregates + weekly alignment ---
    if "y_true" in pred_win.columns:
        agg = pred_win.groupby("grid_id", as_index=False).agg(
            daily_y_pred_mean=("y_pred_mean", "mean"),
            daily_y_true_mean=("y_true", "mean"),
            n_days_crowd=("date", "nunique"),
        )
    else:
        agg = pred_win.groupby("grid_id", as_index=False).agg(
            daily_y_pred_mean=("y_pred_mean", "mean"),
            n_days_crowd=("date", "nunique"),
        )

    base = agg.merge(aln, on="grid_id", how="inner")
    if base.empty:
        raise SystemExit("No overlapping grid_id between daily window and weekly alignment table.")

    for c in POI_COUNT_COLS:
        pct = base[c].rank(method="average", ascending=True, pct=True)
        base[f"{c}_scarcity_q"] = 1.0 - pct

    base["n_days"] = base["n_days_crowd"].astype(int)

    summary_out = here / f"grid_daily_crowd_plus_weekly_poi_alignment_{args.tag}.csv"
    base.to_csv(summary_out, index=False)

    # --- Four category CSV + GPKG (attributes = summary + four scarcity q + focus) ---
    extra_sq = [f"{c}_scarcity_q" for c in POI_COUNT_COLS]
    base_cols = [x for x in base.columns if x not in extra_sq]
    use_cols = base_cols + extra_sq
    use_cols = [x for x in use_cols if x in base.columns]

    for c in POI_COUNT_COLS:
        label = COL2LABEL[c]
        slim = base[use_cols].copy()
        slim.insert(1, "poi_focus_category", label)
        slim.insert(2, "poi_scarcity_q_focus", slim[f"{c}_scarcity_q"])
        cat_csv = here / f"grid_daily_crowd_plus_walign_poi_{label}_{args.tag}.csv"
        slim.to_csv(cat_csv, index=False)

        cat_gpkg = here / f"grid_daily_crowd_plus_walign_poi_{label}_{args.tag}.gpkg"
        layer = f"grid_daily_walign_{label}_{args.tag}"
        cmd = [
            sys.executable,
            str(export_gpkg.relative_to(repo_root)),
            "--grid-weekly",
            args.grid_weekly_parquet,
            "--alignment-csv",
            str(cat_csv.relative_to(repo_root)),
            "--output",
            str(cat_gpkg.relative_to(repo_root)),
            "--layer",
            layer,
        ]
        print("Running:", " ".join(cmd))
        subprocess.run(cmd, cwd=str(repo_root), check=True)
        print(f"Wrote: {cat_csv}")
        print(f"Wrote: {cat_gpkg} (layer={layer})")

    # --- One combined grid GPKG (no category focus) for quick map ---
    combo_gpkg = here / f"grid_daily_crowd_plus_weekly_poi_alignment_{args.tag}.gpkg"
    cmd = [
        sys.executable,
        str(export_gpkg.relative_to(repo_root)),
        "--grid-weekly",
        args.grid_weekly_parquet,
        "--alignment-csv",
        str(summary_out.relative_to(repo_root)),
        "--output",
        str(combo_gpkg.relative_to(repo_root)),
        "--layer",
        f"grid_daily_walign_all_{args.tag}",
    ]
    subprocess.run(cmd, cwd=str(repo_root), check=True)

    print(f"Wrote: {long_out}")
    print(f"Wrote: {summary_out}")
    print(f"Wrote: {combo_gpkg}")


if __name__ == "__main__":
    main()
