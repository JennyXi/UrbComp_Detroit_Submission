$ErrorActionPreference = "Stop"

# Edit this to your local Autoformer repo root (thuml/Autoformer).
$AUTOFORMER_ROOT = "E:\Urban Computing Final Project\autoformer_spatial_0425\Autoformer"

# Use the retrained export script (ratio split default was updated there).
$EXPORT_PY = "E:\Urban Computing Final Project\Try_0412\weekly_retrained_0429_ep40_noearly\export_panel_predictions.py"

# Where your weekly panel CSV lives (same as training input).
$PANEL_CSV = "panel_training_0426/outputs/panel_weekly_top100_2024_2025_topk2024_city_lag1_log1p.csv"

# Checkpoints directory used by your training run.
$CHECKPOINTS_DIR = "panel_training_0426/checkpoints"

# Output directory: this folder.
$OUT_DIR = "weekly_retrained_0505"

# If you know the exact checkpoint folder name, set it here; otherwise leave empty and the exporter will use the latest.
$SETTING = ""

Write-Host "Autoformer root: $AUTOFORMER_ROOT"
Write-Host "Export script:  $EXPORT_PY"
Write-Host "Panel CSV:      $PANEL_CSV"
Write-Host "Checkpoints:    $CHECKPOINTS_DIR"
Write-Host "Out dir:        $OUT_DIR"
Write-Host "Split:          ratio (70/15/15)"

$args = @(
  $EXPORT_PY,
  "--autoformer-root", $AUTOFORMER_ROOT,
  "--panel-csv", $PANEL_CSV,
  "--checkpoints-dir", $CHECKPOINTS_DIR,
  "--out-dir", $OUT_DIR,
  "--split-mode", "ratio",
  "--train-ratio", "0.7",
  "--val-ratio", "0.15",
  "--test-ratio", "0.15",
  "--scope", "test",
  "--target-year", "2025",
  "--seq-len", "24",
  "--label-len", "12",
  "--pred-len", "4",
  "--freq", "w",
  "--target-transform", "log1p"
)

if ($SETTING -ne "") {
  $args += @("--setting", $SETTING)
}

python @args

