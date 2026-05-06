## daily_retrained_0506

This folder contains the **daily** Autoformer retrain (2026-05-06) using **true daily** inputs expanded from `VISITS_BY_DAY`.

### Date split (target dates)

- **Train**: 2025/07/01 ~ 2025/08/30
- **Validation**: 2025/08/31 ~ 2025/09/30
- **Test**: 2025/10/01 ~ 2025/10/30

### Upstream daily parquet (important)

Raw POI parquet is weekly but includes `VISITS_BY_DAY` (Mon..Sun). We expand it into real daily rows and then aggregate to 100m grids.

```cmd
cd /d "E:\Urban Computing Final Project\Try_0412"
python scripts\aggregate_grid_daily_from_visits_by_day.py --date-start 2025-04-01 --date-end 2025-10-30 --output data\grid100_daily_2025_0401_1030_from_byday.parquet
```

### Build daily panel (Top-100)

```cmd
cd /d "E:\Urban Computing Final Project\Try_0412"
python daily_training_0430\build_panel_daily_dataset.py ^
  --input data\grid100_daily_2025_0401_1030_from_byday.parquet ^
  --date-start 2025-04-01 --date-end 2025-10-30 ^
  --top-k 100 --topk-year 2025 ^
  --city-cov lag1 --weekend-cov is_weekend --spatial-cov nbr8_std_lag1 ^
  --target-transform log1p
```

This writes the panel CSV under `panel_training_0426/outputs/` (shared location).

### Train

Run:

- `RUN_TRAIN_DAILY_DATE_SPLIT_0506.cmd`

Outputs:

- Checkpoint under `daily_retrained_0506/checkpoints/`

### Export predictions (test window)

Run:

- `RUN_EXPORT_DAILY_DATE_SPLIT_0506.cmd`

Outputs:

- `daily_retrained_0506/out/panel_pred_test_2025_by_date.csv`
- `daily_retrained_0506/out/panel_pred_test_2025_long.csv`

