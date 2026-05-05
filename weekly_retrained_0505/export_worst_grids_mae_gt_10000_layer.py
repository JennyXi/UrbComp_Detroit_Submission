from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    eval_csv = (
        repo_root
        / "weekly_retrained_0505"
        / "eval_output_weekly_0505_v1_0_38"
        / "eval_per_grid.csv"
    )
    grid_gpkg = repo_root / "POI_Alignment_0429" / "grid100_poi_static_2024.gpkg"
    out_gpkg = repo_root / "weekly_retrained_0505" / "worst_grids_mae_gt_10000.gpkg"

    if not eval_csv.exists():
        raise SystemExit(f"Missing eval CSV: {eval_csv}")
    if not grid_gpkg.exists():
        raise SystemExit(f"Missing grid layer: {grid_gpkg}")

    try:
        import pandas as pd  # type: ignore
        import geopandas as gpd  # type: ignore
    except Exception as e:
        print("This exporter requires geopandas. Install into your venv, e.g.:", file=sys.stderr)
        print(r"  .\.venv\Scripts\pip.exe install geopandas pyogrio", file=sys.stderr)
        raise SystemExit(str(e))

    df = pd.read_csv(eval_csv)
    df["MAE"] = pd.to_numeric(df["MAE"], errors="coerce")
    worst_ids = df.loc[df["MAE"] > 10000, "grid_id"].astype(str).tolist()
    if not worst_ids:
        raise SystemExit("No grids found with MAE > 10000.")

    grids = gpd.read_file(grid_gpkg)
    if "grid_id" not in grids.columns:
        raise SystemExit("grid gpkg missing grid_id column.")
    grids["grid_id"] = grids["grid_id"].astype(str)

    worst = grids[grids["grid_id"].isin(set(worst_ids))].copy()
    worst = worst.merge(df, on="grid_id", how="left")

    out_gpkg.parent.mkdir(parents=True, exist_ok=True)
    worst.to_file(out_gpkg, layer="worst_grids_mae_gt_10000", driver="GPKG")
    print(f"Wrote: {out_gpkg}  rows={len(worst)}")


if __name__ == "__main__":
    main()

