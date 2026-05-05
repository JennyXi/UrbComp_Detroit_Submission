## weekly_retrained_0505

This folder is for **retrained weekly panel Autoformer** outputs using **ratio split** (balanced train/val/test).

### What you will export (after retraining)

The export script will generate files like:

- `panel_pred_test_2025_long_<timestamp>.csv`
- `panel_pred_test_2025_by_date_<timestamp>.csv`

These are the inputs you will later feed into `POI_Alignment_0429/` for alignment.

### One-click export (after you have a checkpoint)

Run:

- `.\RUN_EXPORT_WEEKLY_RATIO_TEST_2025_0505.ps1`

### CMD (recommended on locked-down PowerShell)

From `cmd.exe`:

- Train (ratio split 70/15/15): `weekly_retrained_0505\RUN_TRAIN_WEEKLY_RATIO_0505.cmd`
- Train (tuned, lower val loss): `weekly_retrained_0505\RUN_TRAIN_WEEKLY_RATIO_TUNE_0505.cmd`
- Export test preds (writes `panel_pred_test_2025_long_0505.csv`): `weekly_retrained_0505\RUN_EXPORT_WEEKLY_RATIO_TEST_2025_0505.cmd`

