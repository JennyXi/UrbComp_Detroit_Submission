from __future__ import annotations

import math
from pathlib import Path


def main() -> None:
    repo_root = Path(r"E:\Urban Computing Final Project\Try_0412")

    pred_long = (
        repo_root
        / "daily_retrained_0505"
        / "outputs"
        / "panel_pred_test_2025_long_output_daily_0505_v1.csv"
    )
    pred_by_date = (
        repo_root
        / "daily_retrained_0505"
        / "outputs"
        / "panel_pred_test_2025_by_date_output_daily_0505_v1.csv"
    )
    grid_gpkg = repo_root / "POI_Alignment_0429" / "grid100_poi_static_2024.gpkg"

    out_dir = repo_root / "daily_retrained_0505" / "outputs" / "worst3_daily_oct2025"
    shp_dir = out_dir / "worst3_grids_shp"
    out_shp = shp_dir / "worst3_grids_by_mae_oct2025.shp"

    if not pred_long.exists():
        raise SystemExit(f"Missing predictions CSV: {pred_long}")
    if not pred_by_date.exists():
        raise SystemExit(f"Missing predictions by_date CSV: {pred_by_date}")
    if not grid_gpkg.exists():
        raise SystemExit(f"Missing grid geometry GPKG: {grid_gpkg}")

    import numpy as np
    import pandas as pd

    try:
        import geopandas as gpd  # type: ignore
    except Exception as e:
        raise SystemExit(
            "This exporter requires geopandas. Install into your venv:\n"
            r"  .\.venv\Scripts\pip.exe install geopandas pyogrio"
            f"\n\nOriginal error: {e}"
        )

    # 1) Worst-3 grids by MAE (computed on long rows; Oct 2025 already)
    df = pd.read_csv(pred_long, usecols=["grid_id", "y_true", "y_pred"])
    df["grid_id"] = df["grid_id"].astype(str)

    rows = []
    for gid, sub in df.groupby("grid_id", sort=False):
        yt = sub["y_true"].to_numpy(dtype=np.float64)
        yp = sub["y_pred"].to_numpy(dtype=np.float64)
        e = yp - yt
        mae = float(np.mean(np.abs(e)))
        mse = float(np.mean(e**2))
        rmse = float(math.sqrt(mse))
        bias = float(np.mean(e))
        rows.append({"grid_id": str(gid), "n": int(len(sub)), "MAE": mae, "RMSE": rmse, "MSE": mse, "bias": bias})

    per_grid = pd.DataFrame(rows).sort_values("MAE", ascending=False).reset_index(drop=True)
    worst3 = per_grid.head(3).copy()
    worst_ids = worst3["grid_id"].astype(str).tolist()

    # 2) Export SHP (geometry + metrics)
    grids = gpd.read_file(grid_gpkg)
    grids["grid_id"] = grids["grid_id"].astype(str)
    out = grids.merge(worst3, on="grid_id", how="inner")
    if len(out) == 0:
        raise SystemExit("Join produced 0 rows. Check grid_id formatting.")

    shp_dir.mkdir(parents=True, exist_ok=True)
    out.to_file(out_shp, driver="ESRI Shapefile", encoding="utf-8")

    # 3) Time series plots (daily by_date: True vs Pred(mean))
    ts = pd.read_csv(pred_by_date, parse_dates=["date"])
    ts["grid_id"] = ts["grid_id"].astype(str)
    ts = ts.loc[ts["grid_id"].isin(set(worst_ids))].copy()
    ts = ts.sort_values(["grid_id", "date"]).reset_index(drop=True)

    # enforce Oct 2025 only
    ts = ts.loc[(ts["date"] >= pd.Timestamp("2025-10-01")) & (ts["date"] <= pd.Timestamp("2025-10-31"))]

    import matplotlib.pyplot as plt

    for gid in worst_ids:
        sub = ts.loc[ts["grid_id"] == gid].copy()
        if len(sub) == 0:
            continue
        fig = plt.figure(figsize=(12, 4))
        plt.plot(sub["date"], sub["y_true"], label="True", linewidth=2)
        plt.plot(sub["date"], sub["y_pred_mean"], label="Pred (mean)", linewidth=2)
        plt.title(f"Daily crowd flow (Oct 2025): {gid}")
        plt.xlabel("Date")
        plt.ylabel("Visits")
        plt.grid(True, alpha=0.25)
        plt.legend()
        fig.autofmt_xdate()
        out_png = out_dir / f"daily_crowd_flow_oct2025_{gid}.png"
        out_dir.mkdir(parents=True, exist_ok=True)
        plt.tight_layout()
        plt.savefig(out_png, dpi=160)
        plt.close(fig)

    # Also write a small manifest for convenience
    (out_dir / "worst3_grids_metrics.csv").write_text(worst3.to_csv(index=False), encoding="utf-8")

    print(f"Wrote SHP: {out_shp}  rows={len(out)}")
    print(f"Worst3 grid_ids: {worst_ids}")
    print(f"Wrote plots into: {out_dir}")


if __name__ == "__main__":
    main()

