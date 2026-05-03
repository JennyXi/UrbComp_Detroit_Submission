"""
Join per-grid POI alignment CSV to the 100m grid geometry and write a GPKG for QGIS.

Uses gx/gy from `data/grid100_weekly_2024_2025.parquet` at repository root.
Copy lives in `weekly_alignment/` for submission; resolves paths relative to repo root.

By default only polygons for `grid_id` present in the alignment CSV are exported.
Pass `--all-city-grids` for a city-wide backdrop join.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq
import pyogrio
from shapely.geometry import box

try:
    import geopandas as gpd
except Exception as e:  # pragma: no cover
    raise SystemExit("Missing geopandas. Install with: python -m pip install geopandas") from e


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export grid POI alignment (CSV) as a GPKG layer for QGIS."
    )
    parser.add_argument(
        "--grid-weekly",
        default="data/grid100_weekly_2024_2025.parquet",
        help="Grid-weekly parquet (authoritative grid_id, gx, gy, cell lon/lat).",
    )
    parser.add_argument(
        "--alignment-csv",
        required=True,
        help="Per-grid alignment CSV (e.g. weekly_alignment/alignment_jul_sep_2025.csv).",
    )
    parser.add_argument(
        "--output",
        default="",
        help="Output .gpkg path. Default: same basename as --alignment-csv with .gpkg next to it.",
    )
    parser.add_argument("--layer", default="grid_poi_alignment", help="GPKG layer name.")
    parser.add_argument("--cell-meters", type=float, default=100.0, help="Grid cell size (must match aggregation).")
    parser.add_argument("--epsg", type=int, default=32617, help="CRS EPSG for grid polygons.")
    parser.add_argument(
        "--join",
        choices=["left", "inner"],
        default="left",
        help="Used only with --all-city-grids: left = full parquet + alignment attrs; inner = overlap only.",
    )
    parser.add_argument(
        "--all-city-grids",
        action="store_true",
        help=(
            "Export every distinct grid polygon from the parquet (city-wide). "
            "Default (omit flag): restrict polygons to grid_id rows present in --alignment-csv only."
        ),
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    grid_path = (repo_root / str(args.grid_weekly)).resolve()
    aln_path = Path(args.alignment_csv)
    if not aln_path.is_absolute():
        aln_path = (repo_root / aln_path).resolve()

    if str(args.output).strip():
        out_path = Path(args.output)
        if not out_path.is_absolute():
            out_path = (repo_root / out_path).resolve()
    else:
        out_path = aln_path.with_suffix(".gpkg")

    out_path.parent.mkdir(parents=True, exist_ok=True)

    if not grid_path.exists():
        raise SystemExit(f"Missing --grid-weekly parquet: {grid_path}")
    if not aln_path.exists():
        raise SystemExit(f"Missing --alignment-csv: {aln_path}")

    cell = float(args.cell_meters)
    epsg = int(args.epsg)

    g = pq.read_table(grid_path, columns=["grid_id", "gx", "gy", "cell_lon", "cell_lat"]).to_pandas()
    g["grid_id"] = g["grid_id"].astype(str)
    g["gx"] = pd.to_numeric(g["gx"], errors="coerce").astype("Int64")
    g["gy"] = pd.to_numeric(g["gy"], errors="coerce").astype("Int64")
    g = g.dropna(subset=["gx", "gy"]).copy()
    g["gx"] = g["gx"].astype(int)
    g["gy"] = g["gy"].astype(int)
    grids = g.drop_duplicates(subset=["grid_id", "gx", "gy"])[["grid_id", "gx", "gy", "cell_lon", "cell_lat"]].copy()

    aln = pd.read_csv(aln_path)
    if "grid_id" not in aln.columns:
        raise SystemExit("alignment CSV must contain grid_id.")
    aln["grid_id"] = aln["grid_id"].astype(str)
    csv_ids = set(aln["grid_id"].unique())

    if not args.all_city_grids:
        kept = grids["grid_id"].isin(csv_ids)
        n_before = len(grids)
        grids = grids.loc[kept].copy()
        missing = csv_ids - set(grids["grid_id"].unique())
        if missing:
            print(
                f"Warning: {len(missing)} grid_id(s) from alignment CSV have no row in grid parquet "
                f"(they will be omitted). Example: {next(iter(missing))!s}",
                file=sys.stderr,
            )
        scope_note = f"csv_scope_only rows={len(grids)} (was {n_before} city-wide)"
    else:
        scope_note = "all_city_grids"

    time_scale = "daily" if "n_days" in aln.columns else ("weekly" if "n_weeks" in aln.columns else "unknown")

    if args.all_city_grids:
        if args.join == "left":
            df = grids.merge(aln, on="grid_id", how="left")
        else:
            df = grids.merge(aln, on="grid_id", how="inner")
    else:
        df = grids.merge(aln, on="grid_id", how="inner")

    df.insert(0, "alignment_time_scale", time_scale)
    df.insert(1, "alignment_source_csv", str(aln_path.name))

    geom = [box(gx * cell, gy * cell, (gx + 1) * cell, (gy + 1) * cell) for gx, gy in zip(df["gx"], df["gy"])]
    gdf = gpd.GeoDataFrame(df, geometry=geom, crs=f"EPSG:{epsg}")

    pyogrio.write_dataframe(gdf, out_path, layer=str(args.layer), overwrite=True)
    print(
        f"Wrote: {out_path}  rows={len(gdf)}  crs=EPSG:{epsg}  cell_m={cell}  "
        f"time_scale={time_scale}  scope={scope_note}"
    )


if __name__ == "__main__":
    main()
