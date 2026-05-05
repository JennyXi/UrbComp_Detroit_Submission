@echo off
setlocal enableextensions

REM Weekly training with your previously best weekly feature set (cmp0428_sp8),
REM but with NEW ratio split (70/15/15).
REM This follows your weekly tuning approach: feature ablations first, keep core hyperparams stable.

set "REPO_ROOT=E:\Urban Computing Final Project\Try_0412"
set "PY=%REPO_ROOT%\.venv\Scripts\python.exe"
set "AUTOFORMER_ROOT=E:\Urban Computing Final Project\autoformer_spatial_0425\Autoformer"

set "TRAIN_PY=%REPO_ROOT%\weekly_retrained_0429_ep40_noearly\train_panel_autoformer.py"

REM Best weekly feature set from your closeout notes: cmp0428_sp8
set "PANEL_CSV=panel_training_0426/outputs/panel_weekly_top100_2024_2025_cmp0428_sp8.csv"

REM Keep checkpoints separate from panel_training_0426 baseline
set "CKPT_DIR=weekly_retrained_0505/checkpoints_weekly_sp8"

cd /d "%REPO_ROOT%"

echo === Train weekly (cmp0428_sp8 features) with ratio split 70/15/15 ===
echo panel_csv: %PANEL_CSV%
echo ckpt_dir:  %CKPT_DIR%
echo.

REM Core weekly hyperparams (same family as your earlier weekly runs):
REM 24/12/4 window, dm128, huber1, lr=1e-4, dropout=0.05
"%PY%" "%TRAIN_PY%" ^
  --autoformer-root "%AUTOFORMER_ROOT%" ^
  --panel-csv "%PANEL_CSV%" ^
  --checkpoints-dir "%CKPT_DIR%" ^
  --split-mode ratio --train-ratio 0.7 --val-ratio 0.15 --test-ratio 0.15 ^
  --seq-len 24 --label-len 12 --pred-len 4 --freq w --target-transform log1p ^
  --loss huber --huber-delta 1.0 ^
  --epochs 80 --early-stop --patience 8 --batch-size 64 ^
  --lr 1e-4 --dropout 0.05 --weight-decay 0 --grad-clip-norm 0 ^
  --d-model 128 --e-layers 2 --d-layers 1 --d-ff 512 --moving-avg 25

echo.
echo Done.
endlocal

