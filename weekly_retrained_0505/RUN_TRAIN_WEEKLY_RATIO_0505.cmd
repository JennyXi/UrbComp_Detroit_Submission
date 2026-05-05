@echo off
setlocal enableextensions

REM ====== Edit these paths if needed ======
set "REPO_ROOT=E:\Urban Computing Final Project\Try_0412"
set "PY=%REPO_ROOT%\.venv\Scripts\python.exe"
set "AUTOFORMER_ROOT=E:\Urban Computing Final Project\autoformer_spatial_0425\Autoformer"

REM Training entrypoint (ratio split default already updated, but we pass flags explicitly)
set "TRAIN_PY=%REPO_ROOT%\weekly_retrained_0429_ep40_noearly\train_panel_autoformer.py"

REM Weekly panel CSV (Top-100, 2024-2025, log1p target)
set "PANEL_CSV=panel_training_0426/outputs/panel_weekly_top100_2024_2025_topk2024_city_lag1_log1p.csv"

REM Where checkpoints will be written
set "CKPT_DIR=panel_training_0426/checkpoints"

cd /d "%REPO_ROOT%"

echo === Training weekly panel Autoformer (ratio split 70/15/15) ===
echo repo_root:      %REPO_ROOT%
echo autoformer_root:%AUTOFORMER_ROOT%
echo panel_csv:      %PANEL_CSV%
echo checkpoints:    %CKPT_DIR%
echo.

REM IMPORTANT: We keep the weekly architecture the same as your baseline (24/12/4, dm128).
"%PY%" "%TRAIN_PY%" ^
  --autoformer-root "%AUTOFORMER_ROOT%" ^
  --panel-csv "%PANEL_CSV%" ^
  --checkpoints-dir "%CKPT_DIR%" ^
  --split-mode ratio --train-ratio 0.7 --val-ratio 0.15 --test-ratio 0.15 ^
  --seq-len 24 --label-len 12 --pred-len 4 --freq w --target-transform log1p ^
  --loss huber --huber-delta 1.0 ^
  --d-model 128 --e-layers 2 --d-layers 1 --d-ff 512 --dropout 0.05 --moving-avg 25

echo.
echo Done.
endlocal

