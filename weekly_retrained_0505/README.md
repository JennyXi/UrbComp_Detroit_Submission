## weekly_retrained_0505

This folder contains the **Weekly crowd prediction + POI alignment** artifacts produced on **2026-05-05**.

We train a **shared panel Autoformer** across **Top-100 100m grids** (one model for all grids) and evaluate/align on a
**balanced ratio split** (default **70/15/15** on each grid's time axis, time-ordered).

## Data & scope (weekly)

- **Base observations**: `data/grid100_weekly_2024_2025.parquet`
  - `week_start` is **W-MON** (week starts on Monday)
  - coverage: **2024-01-01 .. 2025-12-29** (105 weeks)
- **Training panel (Top-100)**: weekly panel CSVs under `panel_training_0426/outputs/`
- **Goal**: predict weekly visits per grid for the **test** segment and export per-week predictions with dates

## Split & window (the “ratio” weekly run)

- **Split**: `--split-mode ratio --train-ratio 0.7 --val-ratio 0.15 --test-ratio 0.15`
  - Split is **per-grid time axis**, in time order.
  - With `seq_len=24`, `pred_len=4`, and 105 weeks total, the *targets* date ranges are:
    - Train targets: **2024-06-17 .. 2025-05-26**
    - Val targets: **2025-06-02 .. 2025-09-15**
    - Test targets: **2025-09-22 .. 2025-12-29**
- **Window**:
  - `seq_len=24` (input history = 24 weeks)
  - `label_len=12`
  - `pred_len=4` (forecast horizon = 4 weeks)

## Train (weekly Autoformer, panel shared model)

Preferred entrypoints (CMD-friendly):

- **Baseline**: `RUN_TRAIN_WEEKLY_RATIO_0505.cmd`
- **Tuned**: `RUN_TRAIN_WEEKLY_RATIO_TUNE_0505.cmd`
- **Feature sweep (sp8 set)**: `RUN_TRAIN_WEEKLY_RATIO_SP8_SWEEP_0505.cmd`

Notes:
- Training uses the official Autoformer repo via `--autoformer-root` and imports `models.Autoformer`.
- Loss is Huber on scaled OT (OT is log1p(visits) in the panel CSV).

## Export predictions (weekly)

The exporter writes two tables:

- **Long** (one row per grid × window_start × horizon × date): `panel_pred_test_2025_long_*.csv`
- **By-date** (one row per grid × date): `panel_pred_test_2025_by_date_*.csv`
  - `y_pred_mean`: mean of multiple window forecasts for the same date (**recommended for alignment**)
  - `y_pred_last`: last window forecast for the same date
  - `n_preds`: how many times that date was predicted

CMD:
- Export (ratio, test): `RUN_EXPORT_WEEKLY_RATIO_TEST_2025_0505.cmd`

## Evaluate prediction quality (MAE/RMSE/bias)

We evaluate from the exported **long** table:

```bat
cd /d "E:\Urban Computing Final Project\Try_0412"
.\.venv\Scripts\python.exe weekly_retrained_0429_ep40_noearly\evaluate_panel_predictions.py ^
  --pred-csv weekly_retrained_0505\panel_pred_test_2025_long_output_weekly_0505_v1_0_38.csv ^
  --out-dir weekly_retrained_0505\eval_output_weekly_0505_v1_0_38 ^
  --top-k 15
```

Outputs:
- `eval_summary.txt`: global MAE/RMSE/bias/WAPE/R2 (+ by-horizon)
- `eval_per_grid.csv`: per-grid metrics

## Weekly POI alignment (Oct–Dec 2025)

We align predicted demand to POI supply via Ridge:

1) Compute alignment (writes into `weekly_retrained_0505/alignment/`):

```bat
cd /d "E:\Urban Computing Final Project\Try_0412"
.\.venv\Scripts\python.exe POI_Alignment_0429\compute_alignment.py ^
  --pred-csv "weekly_retrained_0505/out_cmp_citynone/panel_pred_test_2025_by_date_0505_citynone.csv" ^
  --poi-parquet "POI_Alignment_0429/grid100_poi_static_2024.parquet" ^
  --date-start 2025-10-01 --date-end 2025-12-31 ^
  --pred-col y_pred_mean ^
  --ridge-alpha 0.1 --target-log1p ^
  --out-csv "weekly_retrained_0505/alignment/alignment_oct_dec_2025_0505_citynone.csv" ^
  --out-coefs-json "weekly_retrained_0505/alignment/alignment_ridge_coefs_oct_dec_2025_0505_citynone.json"
```

2) Enrich with per-category scarcity + priority labels (ALL grids, no filtering):

```bat
.\.venv\Scripts\python.exe POI_Alignment_0429\summarize_alignment.py ^
  --alignment-csv "weekly_retrained_0505/alignment/alignment_oct_dec_2025_0505_citynone.csv" ^
  --high-positive-quantile 0 ^
  --gate-r-quantile 0 --gate-min-weeks 0 --gate-cbar-quantile 0 --gate-scarcity-q-min 0 ^
  --out-summary-json "weekly_retrained_0505/alignment/alignment_summary_oct_dec_2025_0505_citynone_ALL.json" ^
  --out-top-positive-csv "weekly_retrained_0505/alignment/alignment_top_positive_oct_dec_2025_0505_citynone_ALL.csv" ^
  --out-top-negative-csv "weekly_retrained_0505/alignment/alignment_top_negative_oct_dec_2025_0505_citynone_ALL.csv" ^
  --out-priority-csv "weekly_retrained_0505/alignment/alignment_priority_candidates_oct_dec_2025_0505_citynone_ALL.csv"
```

Key alignment fields (per grid):
- `c_bar`: mean predicted demand in window
- `c_hat`: POI-only fitted demand
- `r_alignment = c_bar - c_hat`
- `priority_q_1/priority_q_2`: recommended POI category priority (quantile scarcity)

## QGIS-ready layers

- Worst-11 grids (MAE > 10000): `weekly_retrained_0505/worst_grids_mae_gt_10000.gpkg`
- Top-100 prediction time table (grid polygons joined with by-date predictions):
  - `weekly_retrained_0505/pred_top100_weekly_by_date_output_weekly_0505_v1_0_38.gpkg`
- Alignment candidates (ALL columns) as GPKG:
  - `weekly_retrained_0505/alignment/alignment_priority_candidates_oct_dec_2025_0505_citynone_ALL.gpkg`


