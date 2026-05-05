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
    out_dir = repo_root / "daily_retrained_0505" / "outputs" / "best3_daily_oct2025"

    if not pred_long.exists():
        raise SystemExit(f"Missing predictions CSV: {pred_long}")
    if not pred_by_date.exists():
        raise SystemExit(f"Missing predictions by_date CSV: {pred_by_date}")

    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt

    # 1) Best-3 grids by MAE (computed on long rows; Oct 2025 already)
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
        rows.append({"grid_id": str(gid), "n": int(len(sub)), "MAE": mae, "RMSE": rmse, "bias": bias})

    per_grid = pd.DataFrame(rows).sort_values("MAE", ascending=True).reset_index(drop=True)
    best3 = per_grid.head(3).copy()
    best_ids = best3["grid_id"].astype(str).tolist()

    # 2) Plot daily time series from by_date
    ts = pd.read_csv(pred_by_date, parse_dates=["date"])
    ts["grid_id"] = ts["grid_id"].astype(str)
    ts = ts.loc[ts["grid_id"].isin(set(best_ids))].copy()
    ts = ts.sort_values(["grid_id", "date"]).reset_index(drop=True)
    ts = ts.loc[(ts["date"] >= pd.Timestamp("2025-10-01")) & (ts["date"] <= pd.Timestamp("2025-10-31"))]

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "best3_grids_metrics.csv").write_text(best3.to_csv(index=False), encoding="utf-8")

    for gid in best_ids:
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
        plt.tight_layout()
        plt.savefig(out_png, dpi=160)
        plt.close(fig)

    print(f"Best3 grid_ids: {best_ids}")
    print(f"Wrote plots into: {out_dir}")


if __name__ == "__main__":
    main()

