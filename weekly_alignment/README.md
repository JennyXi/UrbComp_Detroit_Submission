# Weekly crowd–POI alignment (Jul–Sep 2025)

This folder bundles the **weekly** Ridge alignment analysis for **2025-07-01 … 2025-09-30**: methodology scripts, frozen outputs, and QGIS layers used in the Detroit submission.

## What alignment measures

- **`c_bar`**: Mean of model predictions (`y_pred_mean` by default) over weeks in the window for each 100 m grid (`n_weeks` = distinct weeks).
- **`c_hat`**: Expected activity from **only** the four POI super-category counts, via one joint **Ridge** model on `log1p` POI features (and typically `log1p(c_bar)` as target).
- **`r_alignment`**: `c_bar − c_hat`. Large positive values mean “more predicted crowd than POI supply would suggest”; negative values mean the opposite. There is **one** scalar residual per grid (not four).

## Bundled outputs

| File | Description |
|------|-------------|
| `alignment_jul_sep_2025.csv` | Per-grid table: `c_bar`, `n_weeks`, four `poi_cnt_*`, `c_hat`, `r_alignment`, optional `y_true_bar`. |
| `alignment_ridge_coefs_jul_sep_2025.json` | Ridge coefficients, scaler, intercept, fit metrics, date window. |
| `alignment_summary_jul_sep_2025.json` | Distribution of `r_alignment`, thresholds, action gates. |
| `alignment_top_positive_jul_sep_2025.csv` | Top grids by **high** `r_alignment`. |
| `alignment_top_negative_jul_sep_2025.csv` | Top grids by **low** `r_alignment`. |
| `alignment_priority_candidates_jul_sep_2025.csv` | High-mismatch subset with scarcity scores and `priority_q_*` (planning-oriented). |
| `alignment_jul_sep_2025.gpkg` | QGIS: **100** grids — attributes from the main alignment CSV; layer `grid_poi_alignment_jul_sep`. |
| `alignment_priority_jul_sep_2025.gpkg` | QGIS: **~20** priority grids — attributes from the priority CSV; layer `grid_poi_priority_jul_sep`. |

## Inputs (not duplicated here; live under repo root)

Reproduce from the full repository checkout:

| Input | Typical path |
|-------|----------------|
| Prediction long table | `POI_Alignment_0429/panel_pred_test_2025_by_date.csv` (`grid_id`, `date`, `y_pred_mean`, optional `y_true`) |
| Static POI counts | `POI_Alignment_0429/grid100_poi_static_2024.parquet` |
| Grid geometry index | `data/grid100_weekly_2024_2025.parquet` (for GPKG export) |

## Reproduce (from repository root)

```powershell
cd "E:\Urban Computing Final Project\Try_0412"

# Step 1 — per-grid alignment + coefficients
python weekly_alignment/compute_alignment.py

# Step 2 — summaries, tops, priority table
python weekly_alignment/summarize_alignment.py

# Step 3a — GPKG for all grids in the alignment CSV (~100)
python weekly_alignment/export_alignment_gpkg.py `
  --alignment-csv weekly_alignment/alignment_jul_sep_2025.csv `
  --output weekly_alignment/alignment_jul_sep_2025.gpkg `
  --layer grid_poi_alignment_jul_sep

# Step 3b — GPKG for priority candidates only
python weekly_alignment/export_alignment_gpkg.py `
  --alignment-csv weekly_alignment/alignment_priority_candidates_jul_sep_2025.csv `
  --output weekly_alignment/alignment_priority_jul_sep_2025.gpkg `
  --layer grid_poi_priority_jul_sep
```

Defaults in `compute_alignment.py` / `summarize_alignment.py` target **Jul–Sep 2025** and write into **`weekly_alignment/`**. Override flags as needed (e.g. different `--date-start` / `--date-end`).

### Dependencies

Python 3 with `pandas`, `numpy`, `pyarrow`, `scikit-learn`, and for GPKG export `geopandas`, `pyogrio`, `shapely`.

## Relation to `POI_Alignment_0429/`

The same algorithms exist under `POI_Alignment_0429/` for other date windows. This folder is the **curated Jul–Sep weekly bundle** for submission and reporting.

## GitHub (submission repo)

This bundle was pushed to the **`submission`** remote as branch **`weekly_alignment_jul_sep_2025`** (the remote `main` had diverged and could not be fast-forwarded). Open a PR to merge that branch into `main`, or merge locally after reconciling histories:

https://github.com/JennyXi/UrbComp_Detroit_Submission/pull/new/weekly_alignment_jul_sep_2025
