from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    repo_root = Path(r"E:\Urban Computing Final Project\Try_0412")

    in_csv = (
        repo_root
        / "daily_retrained_0505"
        / "outputs"
        / "panel_pred_test_2025_by_date_output_daily_0505_v1.csv"
    )
    grid_gpkg = repo_root / "POI_Alignment_0429" / "grid100_poi_static_2024.gpkg"
    out_gpkg = (
        repo_root
        / "daily_retrained_0505"
        / "outputs"
        / "panel_pred_test_2025_by_date_output_daily_0505_v1_oct2025.gpkg"
    )

    if not in_csv.exists():
        raise SystemExit(f"Missing CSV: {in_csv}")
    if not grid_gpkg.exists():
        raise SystemExit(f"Missing grid GPKG: {grid_gpkg}")

    try:
        import pandas as pd  # type: ignore
        import geopandas as gpd  # type: ignore
    except Exception as e:
        print("This exporter requires geopandas. Install into your venv:", file=sys.stderr)
        print(r"  .\.venv\Scripts\pip.exe install geopandas pyogrio", file=sys.stderr)
        raise SystemExit(str(e))

    df = pd.read_csv(in_csv, parse_dates=["date"])
    if "grid_id" not in df.columns:
        raise SystemExit("CSV missing required column grid_id")
    df["grid_id"] = df["grid_id"].astype(str)

    # Ensure Oct 2025 only (this file should already be Oct-only, but keep it explicit).
    start = pd.Timestamp("2025-10-01")
    end = pd.Timestamp("2025-10-31")
    df = df.loc[(df["date"] >= start) & (df["date"] <= end)].copy()
    if len(df) == 0:
        raise SystemExit("No rows left after date filter (2025-10-01..2025-10-31).")

    grids = gpd.read_file(grid_gpkg)
    if "grid_id" not in grids.columns:
        raise SystemExit("Grid GPKG missing required column grid_id")
    grids["grid_id"] = grids["grid_id"].astype(str)

    out = grids.merge(df, on="grid_id", how="inner")
    if len(out) == 0:
        raise SystemExit("Join produced 0 rows. Check grid_id formatting.")

    # Keep deterministic ordering for QGIS time slider usage.
    out = out.sort_values(["date", "grid_id"]).reset_index(drop=True)

    out_gpkg.parent.mkdir(parents=True, exist_ok=True)
    out.to_file(out_gpkg, layer="daily_pred_oct2025_by_date", driver="GPKG")
    print(
        f"Wrote: {out_gpkg}  rows={len(out)}  grids={out['grid_id'].nunique()}  "
        f"date_min={out['date'].min().date()}  date_max={out['date'].max().date()}"
    )


if __name__ == "__main__":
    main()

