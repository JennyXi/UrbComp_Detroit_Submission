from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    repo_root = Path(r"E:\Urban Computing Final Project\Try_0412")

    in_csv = (
        repo_root
        / "weekly_retrained_0505"
        / "alignment"
        / "alignment_priority_candidates_oct_dec_2025_0505_citynone_ALL.csv"
    )
    grid_gpkg = repo_root / "POI_Alignment_0429" / "grid100_poi_static_2024.gpkg"
    out_gpkg = (
        repo_root
        / "weekly_retrained_0505"
        / "alignment"
        / "alignment_priority_candidates_oct_dec_2025_0505_citynone_ALL.gpkg"
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

    cand = pd.read_csv(in_csv)
    if "grid_id" not in cand.columns:
        raise SystemExit("CSV missing required column grid_id")
    cand["grid_id"] = cand["grid_id"].astype(str)

    grids = gpd.read_file(grid_gpkg)
    if "grid_id" not in grids.columns:
        raise SystemExit("Grid GPKG missing required column grid_id")
    grids["grid_id"] = grids["grid_id"].astype(str)

    out = grids.merge(cand, on="grid_id", how="inner")
    if len(out) == 0:
        raise SystemExit("Join produced 0 rows. Check grid_id formatting.")

    out_gpkg.parent.mkdir(parents=True, exist_ok=True)
    out.to_file(out_gpkg, layer="alignment_candidates_all", driver="GPKG")
    print(
        f"Wrote: {out_gpkg}  rows={len(out)}  grids={out['grid_id'].nunique()}  "
        f"columns={len(out.columns)}"
    )


if __name__ == "__main__":
    main()

