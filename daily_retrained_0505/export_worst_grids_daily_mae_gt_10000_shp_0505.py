from __future__ import annotations

import math
import sys
from pathlib import Path


def _metrics(y_true, y_pred) -> dict[str, float]:
    import numpy as np

    yt = np.asarray(y_true, dtype=np.float64)
    yp = np.asarray(y_pred, dtype=np.float64)
    e = yp - yt
    mae = float(np.mean(np.abs(e))) if len(e) else float("nan")
    mse = float(np.mean(e**2)) if len(e) else float("nan")
    rmse = float(math.sqrt(mse)) if len(e) else float("nan")
    bias = float(np.mean(e)) if len(e) else float("nan")
    return {"n": float(len(e)), "MAE": mae, "RMSE": rmse, "bias_mean_pred_minus_true": bias}


def main() -> None:
    repo_root = Path(r"E:\Urban Computing Final Project\Try_0412")

    pred_long = (
        repo_root
        / "daily_retrained_0505"
        / "outputs"
        / "panel_pred_test_2025_long_output_daily_0505_v1.csv"
    )
    grid_gpkg = repo_root / "POI_Alignment_0429" / "grid100_poi_static_2024.gpkg"

    out_dir = repo_root / "daily_retrained_0505" / "outputs" / "worst_grids_daily_mae_gt_10000_shp"
    out_shp = out_dir / "worst_grids_daily_mae_gt_10000_oct2025.shp"

    if not pred_long.exists():
        raise SystemExit(f"Missing predictions CSV: {pred_long}")
    if not grid_gpkg.exists():
        raise SystemExit(f"Missing grid geometry GPKG: {grid_gpkg}")

    try:
        import pandas as pd  # type: ignore
        import geopandas as gpd  # type: ignore
    except Exception as e:
        print("This exporter requires geopandas. Install into your venv:", file=sys.stderr)
        print(r"  .\.venv\Scripts\pip.exe install geopandas pyogrio", file=sys.stderr)
        raise SystemExit(str(e))

    df = pd.read_csv(pred_long, usecols=["grid_id", "y_true", "y_pred"])
    df["grid_id"] = df["grid_id"].astype(str)

    rows = []
    for gid, sub in df.groupby("grid_id", sort=False):
        m = _metrics(sub["y_true"].to_numpy(), sub["y_pred"].to_numpy())
        rows.append({"grid_id": str(gid), **m})

    per_grid = pd.DataFrame(rows).sort_values("MAE", ascending=False).reset_index(drop=True)
    worst = per_grid.loc[per_grid["MAE"] > 10000].copy()

    # Weekly exporter typically produced ~11 grids with this threshold.
    # If daily has fewer, fall back to top 11 worst for a non-empty layer.
    if len(worst) == 0:
        worst = per_grid.head(11).copy()

    grids = gpd.read_file(grid_gpkg)
    if "grid_id" not in grids.columns:
        raise SystemExit("Grid GPKG missing required column grid_id")
    grids["grid_id"] = grids["grid_id"].astype(str)

    out = grids.merge(worst, on="grid_id", how="inner")
    if len(out) == 0:
        raise SystemExit("Join produced 0 rows. Check grid_id formatting.")

    out_dir.mkdir(parents=True, exist_ok=True)
    out.to_file(out_shp, driver="ESRI Shapefile", encoding="utf-8")
    print(f"Wrote: {out_shp}  rows={len(out)}")


if __name__ == "__main__":
    main()

