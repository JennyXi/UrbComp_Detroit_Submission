## daily_retrained_0505

Daily panel Autoformer retraining bundle (2026-05-05), aligned to the **same split philosophy** as
`weekly_retrained_0505`: **ratio split 70/15/15** (time-ordered, per-grid timeline).

### Goal

- Train daily Autoformer with **split-mode = ratio**, train/val/test = **0.70 / 0.15 / 0.15**
- Export **test** predictions into:
  - `*_long.csv` (window + horizon level)
  - `*_by_date.csv` (aggregated per `grid_id, date`)

### Important constraint (must match weekly_0505 behavior)

- **Training and exporting MUST use the same split flags**:
  - `--split-mode ratio --train-ratio 0.7 --val-ratio 0.15 --test-ratio 0.15`

If you train with ratio but export with year (or vice versa), you can get wrong evaluation scope or checkpoint mismatch.

### Files in this folder

- `RUN_TRAIN_DAILY_RATIO_BASE_0505.cmd` — train with ratio 70/15/15
- `RUN_EXPORT_DAILY_RATIO_TEST_2025_0505.cmd` — export test predictions with ratio 70/15/15

These scripts call the implementation that already exists in `daily_training_0430/`:
- `daily_training_0430/train_panel_autoformer.py`
- `daily_training_0430/export_panel_predictions.py`

### Autoformer dependency (same as weekly_0505)

Daily training uses the exact same dependency mechanism as weekly: `--autoformer-root` must point to your local **official**
Autoformer checkout (the folder that contains `models/Autoformer.py`).

Your **weekly** scripts already use:

- `E:\Urban Computing Final Project\autoformer_spatial_0425\Autoformer`

The daily CMDs in this folder are wired to the same path.

**Important**: `E:\Urban Computing Final Project\Try_0412\autoformer_spatial_0425\Autoformer` is **not equivalent** on your machine:
its `models/` folder is incomplete, which produces `ModuleNotFoundError: No module named 'models'`.

### Default configuration (base)

This base config follows the daily baseline from `daily_training_0430/README.md`:

- **freq**: `d`
- **window**: `seq_len=84`, `label_len=42`, `pred_len=14` (two-week horizon)
- **model**: `d_model=192`, `e_layers=2`, `d_layers=1`, `d_ff=768`, `dropout=0.08`, `moving_avg=7`
- **loss/optim**: Huber (`--loss huber --huber-delta 1`), AdamW (`lr=5e-5`, `weight_decay=1e-4`), `grad_clip_norm=1.0`
- **training**: early stopping on, `patience=12`, `epochs=40` (upper bound)

If you need to exactly mirror a previously trained checkpoint (e.g. `pred_len=7` and `d_model=256`),
edit the CMDs accordingly — the key here is the split mode and ratios.

### Latest daily_retrained_0505 base (Oct-only output)

为了让导出只覆盖 **2025-10-01 ~ 2025-10-31**，这套 CMD 会对面板数据做时间裁剪：
- `--data-start 2025-04-08`
- `--data-end   2025-10-31`

在导出阶段还会额外过滤：
- `--target-start 2025-10-01`
- `--target-end   2025-10-31`

### How to run (CMD)

Open a CMD window:

```cmd
cd /d "E:\Urban Computing Final Project\Try_0412"
daily_retrained_0505\RUN_TRAIN_DAILY_RATIO_BASE_0505.cmd
```

After training finishes:

```cmd
cd /d "E:\Urban Computing Final Project\Try_0412"
daily_retrained_0505\RUN_EXPORT_DAILY_RATIO_TEST_2025_0505.cmd
```

### Outputs

Under `daily_retrained_0505/outputs/` (and also stable filenames), you will get:

- `panel_pred_test_2025_long.csv` + `panel_pred_test_2025_long_<stamp>.csv`
- `panel_pred_test_2025_by_date.csv` + `panel_pred_test_2025_by_date_<stamp>.csv`

