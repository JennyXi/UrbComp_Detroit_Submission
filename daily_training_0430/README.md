## daily_training_0430

This folder is a snapshot of the **daily panel Autoformer** baseline drafted on **2026-04-30**.

### Daily training code layout

**Thin launchers** (defaults for year-split daily panel):

- `train_panel_autoformer_daily_ratio.py` — calls `train_panel_autoformer.py` (below or under `panel_training_0426/`).
- `export_panel_predictions_daily_ratio.py` — calls `export_panel_predictions.py`.

**Full implementations copied into this folder** (so `daily_training_0430/` alone holds the training/export/build/eval stack relative to repo root):

| File | Role |
|------|------|
| `train_panel_autoformer.py` | Shared Autoformer panel trainer (`freq=d` from launcher). |
| `export_panel_predictions.py` | Exports test predictions to long/by-date CSVs. |
| `build_panel_daily_dataset.py` | Builds Top-K **daily** panel CSV from `data/grid100_daily_*.parquet`. |
| `evaluate_panel_predictions.py` | Metrics from exported preds → `eval_daily_yearsplit/` style outputs. |

Upstream data prep still uses repo-level `scripts/` (e.g. `aggregate_grid_daily.py`) and `data/` parquet paths referenced by `build_panel_daily_dataset.py`.

### Merge with weekly POI alignment

- `export_daily_crowd_with_weekly_poi_alignment.py` — joins daily preds + `weekly_alignment/alignment_jul_sep_2025.csv`; writes combined CSV/GPKG.

### What was trained

- **Task**: daily visits forecasting per 100m grid (Top-100 grids), one shared model across grids.
- **Dataset**: `panel_training_0426/outputs/panel_daily_top100_2024_2025_topk2024_city_lag1_wk_is_weekend_sp_nbr8_std_lag1_log1p.csv`
- **Split**: ratio per-grid timeline (train/val/test = 0.7 / 0.15 / 0.15)
- **Window**: `seq_len=84`, `label_len=42`, `pred_len=14`
- **Model**: Autoformer (`d_model=192`, `e_layers=2`, `d_layers=1`, `d_ff=768`, `dropout=0.08`, `moving_avg=7`)
- **Loss / Optim**: Huber (`delta=1`), AdamW (`lr=5e-5`, `weight_decay=1e-4`), `grad_clip_norm=1.0`
- **Training control**: early stopping enabled, `patience=12`, max `epochs=40`
- **Checkpoint setting**: `panel_Autoformer_ftMS_sl84_ll42_pl14_dm192_el2_dl1_ma7_log1p_huber1`

### How to reproduce (CMD)

Build daily panel (needs `data/grid100_daily_*.parquet` from `scripts/aggregate_grid_daily.py`):

```cmd
cd /d "E:\Urban Computing Final Project\Try_0412"
python daily_training_0430\build_panel_daily_dataset.py
```

Train:

```cmd
cd /d "E:\Urban Computing Final Project\Try_0412"
python daily_training_0430\train_panel_autoformer_daily_ratio.py
```

Export predictions:

```cmd
python daily_training_0430\export_panel_predictions_daily_ratio.py
```

Evaluate (optional):

```cmd
python daily_training_0430\evaluate_panel_predictions.py --pred-csv daily_training_0430/panel_pred_test_2025_long.csv --out-dir daily_training_0430/eval --top-k 15
```

### Daily crowd + weekly POI alignment (Jul–Sep 2025) — CSV + GPKG

The **daily** model predicts day-level `y_pred_mean`. The **weekly** POI alignment table (`weekly_alignment/alignment_jul_sep_2025.csv`) provides `c_bar` / `c_hat` / `r_alignment` and static `poi_cnt_*` from the Ridge method you already froze.

`export_daily_crowd_with_weekly_poi_alignment.py` joins them on `grid_id` (Jul–Sep 2025 window for daily rows), adds per-grid `daily_y_pred_mean` and `n_days_crowd`, recomputes `poi_cnt_*_scarcity_q` in the Top-100 scope, and writes into **this folder**:

| Output | Role |
|--------|------|
| `panel_pred_by_date_walign_jul_sep_2025.csv` | Long format: each daily row + weekly alignment fields (`walign_*`). |
| `grid_daily_crowd_plus_weekly_poi_alignment_jul_sep_2025.csv` | One row per grid: daily Jul–Sep stats + weekly alignment + scarcity_q + `n_days` (GPKG uses **daily** time_scale). |
| `grid_daily_crowd_plus_walign_poi_{life,transport,economy,public_service}_jul_sep_2025.csv` | Grid table per POI category for themed maps. |
| `grid_daily_crowd_plus_walign_poi_*_jul_sep_2025.gpkg` | Four QGIS layers (100 grids each). |
| `grid_daily_crowd_plus_weekly_poi_alignment_jul_sep_2025.gpkg` | Single layer with all attributes. |

```powershell
cd "E:\Urban Computing Final Project\Try_0412"
python daily_training_0430/export_daily_crowd_with_weekly_poi_alignment.py
```

### Accuracy check (2025 test, window-level; OT original scale)

Computed by directly loading the checkpoint and evaluating on the test windows:

- **Overall**: RMSE=22075.595, MAE=1652.716, SMAPE=1.7454, R2=0.3053, N=135800
- **By horizon**: h=14 is the main failure case (RMSE ~ 76645, R2 < 0), while h=1..13 are much better.

