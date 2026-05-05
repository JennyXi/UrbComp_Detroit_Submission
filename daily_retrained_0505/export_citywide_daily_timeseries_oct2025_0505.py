from __future__ import annotations

from pathlib import Path


def main() -> None:
    repo_root = Path(r"E:\Urban Computing Final Project\Try_0412")
    in_csv = (
        repo_root
        / "daily_retrained_0505"
        / "outputs"
        / "panel_pred_test_2025_by_date_output_daily_0505_v1.csv"
    )
    out_png = (
        repo_root
        / "daily_retrained_0505"
        / "outputs"
        / "daily_citywide_crowd_flow_oct2025_output_daily_0505_v1.png"
    )

    if not in_csv.exists():
        raise SystemExit(f"Missing input CSV: {in_csv}")

    import pandas as pd
    import matplotlib.pyplot as plt

    df = pd.read_csv(in_csv, parse_dates=["date"])
    # Ensure Oct 2025 only (this file is already Oct-only, but keep it explicit)
    df = df.loc[(df["date"] >= "2025-10-01") & (df["date"] <= "2025-10-31")].copy()
    if len(df) == 0:
        raise SystemExit("No rows left after date filter (2025-10-01..2025-10-31).")

    agg = (
        df.groupby("date", as_index=False)
        .agg(
            y_true_sum=("y_true", "sum"),
            y_pred_sum=("y_pred_mean", "sum"),
            grids=("grid_id", "nunique"),
        )
        .sort_values("date")
        .reset_index(drop=True)
    )

    fig = plt.figure(figsize=(12, 4))
    plt.plot(agg["date"], agg["y_true_sum"], label="True (sum over grids)", linewidth=2)
    plt.plot(agg["date"], agg["y_pred_sum"], label="Pred (mean, sum over grids)", linewidth=2)
    plt.title("Daily city-wide crowd flow (Detroit, Oct 2025)")
    plt.xlabel("Date")
    plt.ylabel("Visits (sum over Top-100 grids)")
    plt.grid(True, alpha=0.25)
    plt.legend()
    fig.autofmt_xdate()
    plt.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_png, dpi=180)
    plt.close(fig)

    print(f"Wrote: {out_png}  days={len(agg)}  grids_per_day~{int(agg['grids'].median())}")


if __name__ == "__main__":
    main()

