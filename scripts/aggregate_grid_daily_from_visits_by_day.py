"""
Aggregate POI weekly records into a regular grid (default 100m x 100m) x **day**,
by expanding SafeGraph-style `VISITS_BY_DAY` (Mon..Sun) into 7 daily rows.

Why this exists:
- In the upstream parquet, `DATE_RANGE_START` often represents the **week start** (commonly Monday).
- If you aggregate using only `VISIT_COUNTS` at `DATE_RANGE_START`, you get "weekly mass on one day"
  and the remaining 6 days become zeros after panel reindexing.
- This script expands `VISITS_BY_DAY` to produce a true daily long table suitable for
  `daily_training_0430/build_panel_daily_dataset.py`.
"""

from __future__ import annotations

import argparse
import ast
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from pyproj import Transformer


def _parse_visits_by_day(v: object) -> list[float] | None:
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return None
    if isinstance(v, (list, tuple, np.ndarray)):
        try:
            arr = [float(x) for x in v]
        except Exception:
            return None
        return arr
    if isinstance(v, str):
        s = v.strip()
        if not s:
            return None
        try:
            obj = ast.literal_eval(s)
        except Exception:
            return None
        if isinstance(obj, (list, tuple)):
            try:
                return [float(x) for x in obj]
            except Exception:
                return None
    return None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="POI weekly parquet -> grid x day by expanding VISITS_BY_DAY (UTM 17N)."
    )
    parser.add_argument(
        "--input",
        default=r"E:\Urban Computing Final Project\Try_0412\data\detroit_filtered.parquet",
        help="Raw POI parquet containing DATE_RANGE_START and VISITS_BY_DAY.",
    )
    parser.add_argument(
        "--output",
        default=r"E:\Urban Computing Final Project\Try_0412\data\grid100_daily_2024_2025_from_byday.parquet",
        help="Output Parquet (long: date, gx, gy, visits, visitors, cell center lon/lat).",
    )
    parser.add_argument("--date-start", default="2024-01-01")
    parser.add_argument("--date-end", default="2025-12-31")
    parser.add_argument(
        "--cell-meters",
        type=float,
        default=100.0,
        help="Square cell side length in meters (projected CRS).",
    )
    parser.add_argument(
        "--epsg",
        type=int,
        default=32617,
        help="Projected CRS for grid (default 32617 = WGS84 UTM 17N, good for Detroit).",
    )
    parser.add_argument("--batch-rows", type=int, default=50_000)
    parser.add_argument(
        "--week-start",
        default="monday",
        choices=["monday", "unknown"],
        help=(
            "Interpretation of DATE_RANGE_START. If 'monday', offsets 0..6 map to Mon..Sun. "
            "Use 'unknown' only if you plan to validate ordering manually."
        ),
    )
    args = parser.parse_args()

    inp = Path(args.input)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    cell = float(args.cell_meters)
    t0 = pd.Timestamp(args.date_start).normalize()
    t1 = pd.Timestamp(args.date_end).normalize()

    to_proj = Transformer.from_crs("EPSG:4326", f"EPSG:{args.epsg}", always_xy=True)
    to_wgs = Transformer.from_crs(f"EPSG:{args.epsg}", "EPSG:4326", always_xy=True)

    # Partial sums per (date, gx, gy): visits, visitors
    acc: dict[tuple[pd.Timestamp, int, int], list[float]] = defaultdict(lambda: [0.0, 0.0])
    cols = ["DATE_RANGE_START", "LATITUDE", "LONGITUDE", "VISIT_COUNTS", "VISITOR_COUNTS", "VISITS_BY_DAY"]
    pf = pq.ParquetFile(inp)

    for batch in pf.iter_batches(columns=cols, batch_size=args.batch_rows):
        sub = batch.to_pandas()
        if sub.empty:
            continue

        sub["DATE_RANGE_START"] = pd.to_datetime(sub["DATE_RANGE_START"])
        week_start = sub["DATE_RANGE_START"].dt.normalize()

        lat = pd.to_numeric(sub["LATITUDE"], errors="coerce").to_numpy(dtype=np.float64)
        lon = pd.to_numeric(sub["LONGITUDE"], errors="coerce").to_numpy(dtype=np.float64)
        ok = np.isfinite(lat) & np.isfinite(lon) & week_start.notna().to_numpy()
        if not ok.any():
            continue

        sub = sub.loc[ok].copy()
        lat = lat[ok]
        lon = lon[ok]
        week_start = week_start.loc[ok].reset_index(drop=True)

        x, y = to_proj.transform(lon, lat)
        gx = np.floor(np.asarray(x, dtype=np.float64) / cell).astype(np.int64)
        gy = np.floor(np.asarray(y, dtype=np.float64) / cell).astype(np.int64)

        visit_counts = pd.to_numeric(sub["VISIT_COUNTS"], errors="coerce").fillna(0.0).to_numpy(dtype=np.float64)
        visitor_counts = pd.to_numeric(sub["VISITOR_COUNTS"], errors="coerce").fillna(0.0).to_numpy(dtype=np.float64)
        byday_raw = sub["VISITS_BY_DAY"].tolist()

        # Expand each weekly record into up to 7 daily records
        # and accumulate by (day, cell). We do this row-wise to keep memory bounded.
        for i in range(len(sub)):
            ws = pd.Timestamp(week_start.iloc[i])
            arr = _parse_visits_by_day(byday_raw[i])

            if arr is None or len(arr) != 7:
                # Fallback: keep the total on week_start (same behavior as old script)
                day_list = [ws]
                visit_list = [float(visit_counts[i])]
                visitor_list = [float(visitor_counts[i])]
            else:
                # Mon..Sun mapping (common SafeGraph convention). Offsets 0..6.
                day_list = [ws + pd.Timedelta(days=k) for k in range(7)]
                visit_list = [float(max(0.0, v)) for v in arr]

                total_v = float(sum(visit_list))
                tot_visitors = float(max(0.0, visitor_counts[i]))
                if total_v > 0:
                    visitor_list = [tot_visitors * (v / total_v) for v in visit_list]
                else:
                    visitor_list = [0.0] * 7

            for d, v, u in zip(day_list, visit_list, visitor_list):
                if d < t0 or d > t1:
                    continue
                key = (pd.Timestamp(d), int(gx[i]), int(gy[i]))
                a = acc[key]
                a[0] += float(v)
                a[1] += float(u)

    if not acc:
        raise SystemExit("No rows aggregated. Check date range, lat/lon, and input path.")

    rows = []
    for (day, gx0, gy0), vals in sorted(acc.items()):
        visits = float(vals[0])
        visitors = float(vals[1])
        cx = (gx0 + 0.5) * cell
        cy = (gy0 + 0.5) * cell
        clon, clat = to_wgs.transform(cx, cy)
        rows.append(
            {
                "date": day,
                "gx": gx0,
                "gy": gy0,
                "grid_id": f"{gx0}_{gy0}",
                "visits": visits,
                "visitors": visitors,
                "cell_lon": clon,
                "cell_lat": clat,
                "is_weekend": int(pd.Timestamp(day).dayofweek >= 5),
            }
        )

    out_df = pd.DataFrame(rows)
    out_df.to_parquet(out, index=False)
    print(
        f"Wrote {out}  rows={len(out_df)}  cell_m={cell}  epsg={args.epsg}  "
        f"date=[{args.date_start}, {args.date_end}]"
    )


if __name__ == "__main__":
    main()

