## daily_training_0430

This folder is a snapshot of the **daily panel Autoformer** baseline drafted on **2026-04-30**.

### Training / export entrypoints (copied here for submission)

These thin wrappers call `panel_training_0426/train_panel_autoformer.py` and `export_panel_predictions.py` with daily defaults; checkpoints are written under `daily_training_0430/checkpoints/` when you train locally:

- `train_panel_autoformer_daily_ratio.py`
- `export_panel_predictions_daily_ratio.py`

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

Train:

```cmd
cd /d "E:\Urban Computing Final Project\Try_0412"
".\.venv\Scripts\python.exe" -u ".\panel_training_0426\train_panel_autoformer_daily_ratio.py" --autoformer-root "E:\Urban Computing Final Project\autoformer_spatial_0425\Autoformer"
```

Export predictions (if export script runs on your machine):

```cmd
cd /d "E:\Urban Computing Final Project\Try_0412"
".\.venv\Scripts\python.exe" -u ".\panel_training_0426\export_panel_predictions_daily_ratio.py" --autoformer-root "E:\Urban Computing Final Project\autoformer_spatial_0425\Autoformer"
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

